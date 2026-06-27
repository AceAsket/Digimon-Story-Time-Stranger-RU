import fs from "node:fs/promises";
import path from "node:path";

const artifactModule = process.env.ARTIFACT_TOOL_MODULE ?? "@oai/artifact-tool";
const { SpreadsheetFile, Workbook } = await import(artifactModule);

const root = process.cwd();
const inputJson = path.join(root, "exports", "translation_quality_audit_v023.json");
const outputXlsx = path.join(root, "exports", "translation_quality_audit_v023.xlsx");
const previewDir = path.join(root, "verify", "translation_quality_audit_v023");

const rows = JSON.parse(await fs.readFile(inputJson, "utf8"));

const headers = [
  "severity",
  "category",
  "reason",
  "package",
  "file",
  "key",
  "speaker",
  "current_ru",
  "source_en",
  "suggested_action",
];

function countBy(items, selector) {
  const map = new Map();
  for (const item of items) {
    const key = selector(item);
    map.set(key, (map.get(key) ?? 0) + 1);
  }
  return map;
}

function safeSheetName(value) {
  return value.replace(/[\\/*?:[\]]/g, " ").slice(0, 31);
}

function colLetter(index) {
  let n = index + 1;
  let out = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    out = String.fromCharCode(65 + rem) + out;
    n = Math.floor((n - 1) / 26);
  }
  return out;
}

function matrixFromRows(items) {
  return [headers, ...items.map((row) => headers.map((key) => row[key] ?? ""))];
}

function writeTable(sheet, topLeft, matrix, tableName) {
  const rowCount = matrix.length;
  const colCount = matrix[0].length;
  const range = sheet.getRangeByIndexes(topLeft.row, topLeft.col, rowCount, colCount);
  range.values = matrix;
  const start = `${colLetter(topLeft.col)}${topLeft.row + 1}`;
  const end = `${colLetter(topLeft.col + colCount - 1)}${topLeft.row + rowCount}`;
  const table = sheet.tables.add(`${start}:${end}`, true, tableName);
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  sheet.freezePanes.freezeRows(1);
  range.format.wrapText = true;
  range.format.verticalAlignment = "top";
  sheet.getRangeByIndexes(topLeft.row, topLeft.col, 1, colCount).format.font = { bold: true, color: "#FFFFFF" };
  return range;
}

function applyAuditWidths(sheet, rowCount) {
  const widths = [9, 14, 26, 18, 38, 26, 22, 82, 82, 34];
  widths.forEach((width, col) => {
    sheet.getRangeByIndexes(0, col, Math.max(rowCount, 1), 1).format.columnWidth = width;
  });
}

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const packageCounts = workbook.worksheets.add("Package Counts");
const actionQueue = workbook.worksheets.add("Action Queue");
const candidates = workbook.worksheets.add("Candidates");

const byCategory = countBy(rows, (row) => row.category);
const byPackageCategory = countBy(rows, (row) => `${row.package}\t${row.category}`);
const byPackage = [...new Set(rows.map((row) => row.package))].sort();
const byFile = [...countBy(rows, (row) => `${row.package}/${row.file}`).entries()]
  .map(([file, count]) => ({ file, count }))
  .sort((a, b) => b.count - a.count || a.file.localeCompare(b.file))
  .slice(0, 40);

const summaryMatrix = [
  ["Translation QA Audit", ""],
  ["Generated", `UTC ${new Date().toISOString()}`],
  ["Total candidates", rows.length],
  ["Untranslated", byCategory.get("untranslated") ?? 0],
  ["Machine-like", byCategory.get("machine") ?? 0],
  ["Gender risk", byCategory.get("gender") ?? 0],
  ["Encoding", byCategory.get("encoding") ?? 0],
  ["", ""],
  ["Top files", "Candidates"],
  ...byFile.map((item) => [item.file, item.count]),
];
summary.getRangeByIndexes(0, 0, summaryMatrix.length, 2).values = summaryMatrix;
summary.getRange("A1:B1").format.font = { bold: true, size: 16, color: "#1F2937" };
summary.getRange("A3:B7").format.borders = { preset: "all", style: "thin", color: "#D1D5DB" };
summary.getRange("A9:B49").format.borders = { preset: "all", style: "thin", color: "#E5E7EB" };
summary.getRange("A:B").format.wrapText = true;
summary.getRange("A:A").format.columnWidth = 62;
summary.getRange("B:B").format.columnWidth = 18;
summary.showGridLines = false;

const packageMatrix = [
  ["package", "untranslated", "machine", "gender", "encoding", "total"],
  ...byPackage.map((pkg) => {
    const untranslated = byPackageCategory.get(`${pkg}\tuntranslated`) ?? 0;
    const machine = byPackageCategory.get(`${pkg}\tmachine`) ?? 0;
    const gender = byPackageCategory.get(`${pkg}\tgender`) ?? 0;
    const encoding = byPackageCategory.get(`${pkg}\tencoding`) ?? 0;
    return [pkg, untranslated, machine, gender, encoding, untranslated + machine + gender + encoding];
  }),
];
writeTable(packageCounts, { row: 0, col: 0 }, packageMatrix, "PackageCounts");
packageCounts.getRange("A:F").format.columnWidth = 18;
packageCounts.showGridLines = false;

const actionRows = rows
  .filter((row) => row.package !== "app_text01" || row.category !== "untranslated")
  .sort((a, b) => {
    const packageWeight = (pkg) => (pkg === "patch_text01" ? 0 : pkg.startsWith("addcont_") ? 1 : 2);
    return (
      packageWeight(a.package) - packageWeight(b.package) ||
      Number(b.severity) - Number(a.severity) ||
      a.category.localeCompare(b.category) ||
      a.file.localeCompare(b.file) ||
      a.key.localeCompare(b.key)
    );
  })
  .slice(0, 1500);
const actionMatrix = matrixFromRows(actionRows);
writeTable(actionQueue, { row: 0, col: 0 }, actionMatrix, "ActionQueue");
applyAuditWidths(actionQueue, actionMatrix.length);
actionQueue.showGridLines = false;

const candidateMatrix = matrixFromRows(rows);
writeTable(candidates, { row: 0, col: 0 }, candidateMatrix, "Candidates");
applyAuditWidths(candidates, candidateMatrix.length);
candidates.showGridLines = false;

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputXlsx);

await fs.mkdir(previewDir, { recursive: true });
const previewRanges = {
  Summary: "A1:B50",
  "Package Counts": "A1:F20",
  "Action Queue": "A1:J45",
};
for (const sheetName of ["Summary", "Package Counts", "Action Queue"]) {
  const preview = await workbook.render({ sheetName: safeSheetName(sheetName), range: previewRanges[sheetName], scale: 1, format: "png" });
  const bytes = new Uint8Array(await preview.arrayBuffer());
  await fs.writeFile(path.join(previewDir, `${sheetName.replaceAll(" ", "_")}.png`), bytes);
}

const inspection = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 6000,
  tableMaxRows: 5,
  tableMaxCols: 8,
  tableMaxCellChars: 90,
});
await fs.writeFile(path.join(previewDir, "inspect.json"), JSON.stringify(inspection, null, 2), "utf8");
await fs.rm(`${outputXlsx}.inspect.ndjson`, { force: true });

console.log(`wrote=${outputXlsx}`);
console.log(`previews=${previewDir}`);
console.log(`rows=${rows.length}`);
console.log(`action_rows=${actionRows.length}`);

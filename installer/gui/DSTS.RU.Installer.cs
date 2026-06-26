using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DstsRuInstaller
{
    internal static class Program
    {
        [STAThread]
        private static int Main(string[] args)
        {
            InstallerCore core = new InstallerCore(AppDomain.CurrentDomain.BaseDirectory);

            try
            {
                if (args.Length >= 2 && IsSwitch(args[0], "install"))
                {
                    core.Install(args[1], null);
                    return 0;
                }
                if (args.Length >= 2 && IsSwitch(args[0], "restore"))
                {
                    core.RestoreLatest(args[1], null);
                    return 0;
                }
            }
            catch
            {
                return 1;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm(core));
            return 0;
        }

        private static bool IsSwitch(string value, string name)
        {
            return string.Equals(value, "/" + name, StringComparison.OrdinalIgnoreCase)
                || string.Equals(value, "--" + name, StringComparison.OrdinalIgnoreCase);
        }
    }

    internal sealed class MainForm : Form
    {
        private readonly InstallerCore core;
        private readonly TextBox pathTextBox;
        private readonly TextBox logTextBox;
        private readonly Button browseButton;
        private readonly Button detectButton;
        private readonly Button installButton;
        private readonly Button restoreButton;
        private readonly Button backupsButton;

        public MainForm(InstallerCore core)
        {
            this.core = core;

            Text = "Digimon Story Time Stranger RU - установщик";
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(760, 660);
            Size = new Size(860, 700);
            Font = new Font("Segoe UI", 9F);
            BackColor = Color.FromArgb(246, 248, 252);
            Icon associatedIcon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            if (associatedIcon != null)
            {
                Icon = associatedIcon;
            }

            PictureBox banner = new PictureBox();
            banner.Anchor = AnchorStyles.Left | AnchorStyles.Top | AnchorStyles.Right;
            banner.Location = new Point(0, 0);
            banner.Size = new Size(ClientSize.Width, 170);
            banner.SizeMode = PictureBoxSizeMode.StretchImage;
            banner.Image = LoadImageResource("DstsRuInstaller.banner.png");
            Controls.Add(banner);

            Label title = new Label();
            title.Text = "Digimon Story Time Stranger RU";
            title.Font = new Font(Font.FontFamily, 16F, FontStyle.Bold);
            title.ForeColor = Color.White;
            title.BackColor = Color.Transparent;
            title.AutoSize = true;
            title.Location = new Point(22, 24);
            banner.Controls.Add(title);

            Label subtitle = new Label();
            subtitle.Text = "Русский перевод";
            subtitle.Font = new Font(Font.FontFamily, 10F, FontStyle.Regular);
            subtitle.ForeColor = Color.FromArgb(225, 238, 255);
            subtitle.BackColor = Color.Transparent;
            subtitle.AutoSize = true;
            subtitle.Location = new Point(24, 58);
            banner.Controls.Add(subtitle);

            Label pathLabel = new Label();
            pathLabel.Text = "Папка игры";
            pathLabel.AutoSize = true;
            pathLabel.Location = new Point(20, 195);
            Controls.Add(pathLabel);

            pathTextBox = new TextBox();
            pathTextBox.Anchor = AnchorStyles.Left | AnchorStyles.Top | AnchorStyles.Right;
            pathTextBox.Location = new Point(23, 219);
            pathTextBox.Size = new Size(560, 24);
            Controls.Add(pathTextBox);

            browseButton = new Button();
            browseButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            browseButton.Text = "Обзор...";
            browseButton.Location = new Point(596, 217);
            browseButton.Size = new Size(86, 28);
            browseButton.Click += delegate { BrowseForGameDir(); };
            Controls.Add(browseButton);

            detectButton = new Button();
            detectButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            detectButton.Text = "Автонайти";
            detectButton.Location = new Point(690, 217);
            detectButton.Size = new Size(96, 28);
            detectButton.Click += delegate { DetectGameDir(true); };
            Controls.Add(detectButton);

            installButton = new Button();
            installButton.Text = "Установить перевод";
            installButton.Location = new Point(23, 263);
            installButton.Size = new Size(170, 34);
            installButton.Click += delegate { RunOperation(false); };
            Controls.Add(installButton);

            restoreButton = new Button();
            restoreButton.Text = "Восстановить бэкап";
            restoreButton.Location = new Point(205, 263);
            restoreButton.Size = new Size(170, 34);
            restoreButton.Click += delegate { RunOperation(true); };
            Controls.Add(restoreButton);

            backupsButton = new Button();
            backupsButton.Text = "Открыть бэкапы";
            backupsButton.Location = new Point(387, 263);
            backupsButton.Size = new Size(150, 34);
            backupsButton.Click += delegate { OpenBackups(); };
            Controls.Add(backupsButton);

            logTextBox = new TextBox();
            logTextBox.Anchor = AnchorStyles.Left | AnchorStyles.Top | AnchorStyles.Right | AnchorStyles.Bottom;
            logTextBox.Location = new Point(23, 317);
            logTextBox.Multiline = true;
            logTextBox.ReadOnly = true;
            logTextBox.ScrollBars = ScrollBars.Vertical;
            logTextBox.Size = new Size(763, 300);
            logTextBox.BackColor = Color.White;
            Controls.Add(logTextBox);

            Load += delegate
            {
                Log("Payload: " + core.PayloadDescription);
                DetectGameDir(false);
            };
        }

        private static Image LoadImageResource(string name)
        {
            Stream stream = Assembly.GetExecutingAssembly().GetManifestResourceStream(name);
            if (stream == null)
            {
                return null;
            }
            return Image.FromStream(stream);
        }

        private void BrowseForGameDir()
        {
            using (FolderBrowserDialog dialog = new FolderBrowserDialog())
            {
                dialog.Description = "Выберите корневую папку игры";
                dialog.ShowNewFolderButton = false;
                if (Directory.Exists(pathTextBox.Text))
                {
                    dialog.SelectedPath = pathTextBox.Text;
                }

                if (dialog.ShowDialog(this) == DialogResult.OK)
                {
                    pathTextBox.Text = dialog.SelectedPath;
                    ValidateSelectedDir();
                }
            }
        }

        private void DetectGameDir(bool showMessage)
        {
            string detected = core.FindGameDir();
            if (!string.IsNullOrEmpty(detected))
            {
                pathTextBox.Text = detected;
                Log("Найдена папка игры: " + detected);
                ValidateSelectedDir();
            }
            else if (showMessage)
            {
                MessageBox.Show(this, "Автоматически найти папку игры не удалось. Выберите её вручную.", "Папка не найдена", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                Log("Автопоиск не нашёл игру. Укажите папку вручную.");
            }
        }

        private bool ValidateSelectedDir()
        {
            string dir = pathTextBox.Text.Trim();
            if (!Directory.Exists(dir))
            {
                Log("Папка не найдена: " + dir);
                return false;
            }

            try
            {
                core.ValidateGameDir(dir);
                Log("Папка подходит: " + dir);
                return true;
            }
            catch (Exception ex)
            {
                Log("Проверка не прошла: " + ex.Message);
                return false;
            }
        }

        private void RunOperation(bool restore)
        {
            string dir = pathTextBox.Text.Trim();
            if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir))
            {
                MessageBox.Show(this, "Выберите существующую папку игры.", "Нужна папка игры", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            SetBusy(true);
            Log(restore ? "Восстановление последнего бэкапа..." : "Установка перевода...");

            Task.Factory.StartNew(delegate
            {
                if (restore)
                {
                    core.RestoreLatest(dir, LogFromWorker);
                }
                else
                {
                    core.Install(dir, LogFromWorker);
                }
            }).ContinueWith(delegate(Task task)
            {
                BeginInvoke((Action)delegate
                {
                    SetBusy(false);
                    if (task.Exception != null)
                    {
                        Exception ex = task.Exception.GetBaseException();
                        Log("Ошибка: " + ex.Message);
                        MessageBox.Show(this, ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                    else
                    {
                        string message = restore ? "Бэкап восстановлен." : "Перевод установлен. Оригинальные файлы сохранены в бэкап.";
                        Log(message);
                        MessageBox.Show(this, message, "Готово", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                });
            });
        }

        private void OpenBackups()
        {
            string dir = pathTextBox.Text.Trim();
            if (string.IsNullOrEmpty(dir))
            {
                return;
            }

            string backups = Path.Combine(dir, "_dsts_ru_backups");
            if (!Directory.Exists(backups))
            {
                MessageBox.Show(this, "Папка бэкапов пока не создана.", "Бэкапы", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            Process.Start(backups);
        }

        private void SetBusy(bool busy)
        {
            browseButton.Enabled = !busy;
            detectButton.Enabled = !busy;
            installButton.Enabled = !busy;
            restoreButton.Enabled = !busy;
            backupsButton.Enabled = !busy;
            pathTextBox.Enabled = !busy;
            Cursor = busy ? Cursors.WaitCursor : Cursors.Default;
        }

        private void LogFromWorker(string message)
        {
            BeginInvoke((Action)delegate { Log(message); });
        }

        private void Log(string message)
        {
            logTextBox.AppendText("[" + DateTime.Now.ToString("HH:mm:ss") + "] " + message + Environment.NewLine);
        }
    }

    internal sealed class InstallerCore
    {
        private static readonly string[] RequiredPayloadFiles = new[]
        {
            "app_text01.dx11.mvgl",
            "patch_text01.dx11.mvgl"
        };

        private static readonly string[] OptionalPayloadFiles = new[]
        {
            "addcont_01_text01.dx11.mvgl",
            "addcont_02_text01.dx11.mvgl",
            "addcont_03_text01.dx11.mvgl",
            "addcont_05_text01.dx11.mvgl",
            "addcont_07_text01.dx11.mvgl",
            "addcont_12_text01.dx11.mvgl",
            "addcont_17_text01.dx11.mvgl"
        };

        private static readonly string[] PayloadFiles = RequiredPayloadFiles.Concat(OptionalPayloadFiles).ToArray();
        private const string PayloadResourcePrefix = "DstsRuPayload.";

        public readonly string BaseDir;
        public readonly string PayloadDir;
        private readonly HashSet<string> embeddedPayloadFiles;

        public InstallerCore(string baseDir)
        {
            BaseDir = Path.GetFullPath(baseDir);
            PayloadDir = Path.Combine(BaseDir, "payload");
            embeddedPayloadFiles = new HashSet<string>(
                Assembly.GetExecutingAssembly()
                    .GetManifestResourceNames()
                    .Where(name => name.StartsWith(PayloadResourcePrefix, StringComparison.Ordinal))
                    .Select(name => name.Substring(PayloadResourcePrefix.Length)),
                StringComparer.OrdinalIgnoreCase);
        }

        public bool HasEmbeddedPayload
        {
            get { return embeddedPayloadFiles.Count > 0; }
        }

        public string PayloadDescription
        {
            get
            {
                if (HasEmbeddedPayload)
                {
                    return "встроен в установщик";
                }
                return PayloadDir;
            }
        }

        public string FindGameDir()
        {
            foreach (string common in FindSteamCommonDirs())
            {
                string[] candidates = new[]
                {
                    Path.Combine(common, "Digimon Story Time Stranger"),
                    Path.Combine(common, "Digimon Story Time Stranger Demo")
                };

                foreach (string candidate in candidates)
                {
                    if (Directory.Exists(candidate))
                    {
                        return Path.GetFullPath(candidate);
                    }
                }
            }

            return null;
        }

        public void ValidateGameDir(string root)
        {
            string fullRoot = Path.GetFullPath(root);
            foreach (string file in RequiredPayloadFiles)
            {
                FindTargetFile(fullRoot, file);
            }
        }

        public void Install(string root, Action<string> log)
        {
            string fullRoot = Path.GetFullPath(root);
            EnsurePayloadExists();
            ValidateGameDir(fullRoot);

            string backupDir = Path.Combine(fullRoot, "_dsts_ru_backups", DateTime.Now.ToString("yyyyMMdd-HHmmss"));
            Directory.CreateDirectory(backupDir);

            List<ManifestEntry> entries = new List<ManifestEntry>();
            foreach (string file in PayloadFiles)
            {
                bool optional = OptionalPayloadFiles.Contains(file);
                if (optional && !HasPayloadFile(file))
                {
                    continue;
                }

                string target = FindTargetFile(fullRoot, file, optional);
                if (target == null)
                {
                    Log(log, "Опциональный файл не найден в игре, пропуск: " + file);
                    continue;
                }
                string relative = GetRelativePath(fullRoot, target);
                string backupFile = Path.Combine(backupDir, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(backupFile));

                Log(log, "Бэкап: " + relative);
                File.Copy(target, backupFile, true);

                Log(log, "Установка: " + relative);
                CopyPayloadFile(file, target);

                entries.Add(new ManifestEntry(relative, backupFile));
            }

            File.WriteAllText(Path.Combine(backupDir, "manifest.json"), BuildManifest(fullRoot, entries), new UTF8Encoding(false));
            Log(log, "Готово. Бэкап сохранён: " + backupDir);
        }

        public void RestoreLatest(string root, Action<string> log)
        {
            string fullRoot = Path.GetFullPath(root);
            string backupRoot = Path.Combine(fullRoot, "_dsts_ru_backups");
            if (!Directory.Exists(backupRoot))
            {
                throw new InvalidOperationException("Папка бэкапов не найдена: " + backupRoot);
            }

            DirectoryInfo latest = new DirectoryInfo(backupRoot)
                .GetDirectories()
                .OrderByDescending(d => d.Name)
                .FirstOrDefault();

            if (latest == null)
            {
                throw new InvalidOperationException("Бэкапы не найдены в " + backupRoot);
            }

            foreach (FileInfo file in EnumerateFilesSafe(latest.FullName, "*"))
            {
                if (string.Equals(file.Name, "manifest.json", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                string relative = GetRelativePath(latest.FullName, file.FullName);
                string target = Path.Combine(fullRoot, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(target));
                Log(log, "Восстановление: " + relative);
                File.Copy(file.FullName, target, true);
            }

            Log(log, "Восстановлен бэкап: " + latest.FullName);
        }

        private void EnsurePayloadExists()
        {
            if (HasEmbeddedPayload)
            {
                foreach (string file in RequiredPayloadFiles)
                {
                    if (!embeddedPayloadFiles.Contains(file))
                    {
                        throw new InvalidOperationException("Во встроенном payload не найден файл: " + file);
                    }
                }
                return;
            }

            if (!Directory.Exists(PayloadDir))
            {
                throw new InvalidOperationException("Не найдена папка payload рядом с установщиком: " + PayloadDir);
            }

            foreach (string file in RequiredPayloadFiles)
            {
                string payloadFile = Path.Combine(PayloadDir, file);
                if (!File.Exists(payloadFile))
                {
                    throw new InvalidOperationException("Не найден файл payload: " + payloadFile);
                }
            }
        }

        private bool HasPayloadFile(string file)
        {
            if (HasEmbeddedPayload)
            {
                return embeddedPayloadFiles.Contains(file);
            }
            return File.Exists(Path.Combine(PayloadDir, file));
        }

        private void CopyPayloadFile(string file, string target)
        {
            if (HasEmbeddedPayload)
            {
                string resourceName = PayloadResourcePrefix + file;
                using (Stream input = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName))
                {
                    if (input == null)
                    {
                        throw new InvalidOperationException("Во встроенном payload не найден файл: " + file);
                    }
                    using (FileStream output = File.Create(target))
                    {
                        input.CopyTo(output);
                    }
                }
                return;
            }

            File.Copy(Path.Combine(PayloadDir, file), target, true);
        }

        private string FindTargetFile(string root, string fileName, bool optional = false)
        {
            List<string> matches = EnumerateFilesSafe(root, fileName)
                .Select(f => f.FullName)
                .Where(path => !path.Contains("\\_dsts_ru_backups\\") && !path.Contains("\\payload\\"))
                .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
                .ToList();

            if (matches.Count == 0)
            {
                if (optional)
                {
                    return null;
                }
                throw new InvalidOperationException("Не найден файл " + fileName + " внутри " + root + ". Укажите корневую папку игры.");
            }

            return matches[0];
        }

        private static IEnumerable<FileInfo> EnumerateFilesSafe(string root, string pattern)
        {
            Stack<DirectoryInfo> pending = new Stack<DirectoryInfo>();
            pending.Push(new DirectoryInfo(root));

            while (pending.Count > 0)
            {
                DirectoryInfo dir = pending.Pop();
                FileInfo[] files = new FileInfo[0];
                DirectoryInfo[] children = new DirectoryInfo[0];

                try
                {
                    files = dir.GetFiles(pattern);
                }
                catch
                {
                    files = new FileInfo[0];
                }

                foreach (FileInfo file in files)
                {
                    yield return file;
                }

                try
                {
                    children = dir.GetDirectories();
                }
                catch
                {
                    children = new DirectoryInfo[0];
                }

                foreach (DirectoryInfo child in children)
                {
                    if (string.Equals(child.Name, "_dsts_ru_backups", StringComparison.OrdinalIgnoreCase)
                        || string.Equals(child.Name, "payload", StringComparison.OrdinalIgnoreCase))
                    {
                        continue;
                    }
                    pending.Push(child);
                }
            }
        }

        private static IEnumerable<string> FindSteamCommonDirs()
        {
            HashSet<string> result = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            string[] registryPaths = new[]
            {
                @"Software\Valve\Steam",
                @"Software\WOW6432Node\Valve\Steam"
            };

            foreach (RegistryKey root in new[] { Registry.CurrentUser, Registry.LocalMachine })
            {
                foreach (string registryPath in registryPaths)
                {
                    using (RegistryKey key = root.OpenSubKey(registryPath))
                    {
                        if (key == null)
                        {
                            continue;
                        }

                        string steamPath = Convert.ToString(key.GetValue("SteamPath") ?? key.GetValue("InstallPath"));
                        if (string.IsNullOrEmpty(steamPath) || !Directory.Exists(steamPath))
                        {
                            continue;
                        }

                        AddCommonDir(result, Path.Combine(steamPath, @"steamapps\common"));
                        string libraryFile = Path.Combine(steamPath, @"steamapps\libraryfolders.vdf");
                        if (File.Exists(libraryFile))
                        {
                            string content = File.ReadAllText(libraryFile);
                            foreach (Match match in Regex.Matches(content, "\"path\"\\s+\"([^\"]+)\""))
                            {
                                string library = match.Groups[1].Value.Replace(@"\\", @"\");
                                AddCommonDir(result, Path.Combine(library, @"steamapps\common"));
                            }
                        }
                    }
                }
            }

            return result;
        }

        private static void AddCommonDir(HashSet<string> result, string path)
        {
            if (Directory.Exists(path))
            {
                result.Add(Path.GetFullPath(path));
            }
        }

        private static string GetRelativePath(string basePath, string childPath)
        {
            string fullBase = Path.GetFullPath(basePath).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
            string fullChild = Path.GetFullPath(childPath);
            if (fullChild.StartsWith(fullBase, StringComparison.OrdinalIgnoreCase))
            {
                return fullChild.Substring(fullBase.Length);
            }
            return Path.GetFileName(childPath);
        }

        private static string BuildManifest(string gameDir, List<ManifestEntry> entries)
        {
            StringBuilder builder = new StringBuilder();
            builder.AppendLine("{");
            builder.AppendLine("  \"mod\": \"Digimon Story Time Stranger RU\",");
            builder.AppendLine("  \"created_at\": \"" + JsonEscape(DateTime.Now.ToString("o")) + "\",");
            builder.AppendLine("  \"game_dir\": \"" + JsonEscape(gameDir) + "\",");
            builder.AppendLine("  \"files\": [");
            for (int i = 0; i < entries.Count; i++)
            {
                ManifestEntry entry = entries[i];
                builder.AppendLine("    {");
                builder.AppendLine("      \"relative_path\": \"" + JsonEscape(entry.RelativePath) + "\",");
                builder.AppendLine("      \"backup_path\": \"" + JsonEscape(entry.BackupPath) + "\"");
                builder.Append("    }");
                if (i + 1 < entries.Count)
                {
                    builder.Append(",");
                }
                builder.AppendLine();
            }
            builder.AppendLine("  ]");
            builder.AppendLine("}");
            return builder.ToString();
        }

        private static string JsonEscape(string value)
        {
            return value.Replace("\\", "\\\\").Replace("\"", "\\\"");
        }

        private static void Log(Action<string> log, string message)
        {
            if (log != null)
            {
                log(message);
            }
        }
    }

    internal sealed class ManifestEntry
    {
        public readonly string RelativePath;
        public readonly string BackupPath;

        public ManifestEntry(string relativePath, string backupPath)
        {
            RelativePath = relativePath;
            BackupPath = backupPath;
        }
    }
}

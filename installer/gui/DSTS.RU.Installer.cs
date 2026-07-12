using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Reflection;
using System.Security.Cryptography;
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
        private readonly Button updateButton;

        public MainForm(InstallerCore core)
        {
            this.core = core;

            Text = "Digimon Story Time Stranger RU - установщик v" + InstallerMetadata.Version;
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
            pathTextBox.Size = new Size(500, 24);
            Controls.Add(pathTextBox);

            browseButton = new Button();
            browseButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            browseButton.Text = "Обзор...";
            browseButton.Location = new Point(536, 217);
            browseButton.Size = new Size(86, 28);
            browseButton.Click += delegate { BrowseForGameDir(); };
            Controls.Add(browseButton);

            detectButton = new Button();
            detectButton.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            detectButton.Text = "Найти автоматически";
            detectButton.Location = new Point(630, 217);
            detectButton.Size = new Size(156, 28);
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

            updateButton = new Button();
            updateButton.Text = "Проверить обновления";
            updateButton.Location = new Point(549, 263);
            updateButton.Size = new Size(190, 34);
            updateButton.Click += delegate { CheckForUpdates(true); };
            Controls.Add(updateButton);

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
                Log("Версия установщика: " + InstallerMetadata.Version);
                Log("Payload: " + core.PayloadDescription);
                DetectGameDir(false);
                CheckForUpdates(false);
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
                        string message = restore
                            ? "Бэкап восстановлен."
                            : "Перевод установлен. Оригинальные файлы сохранены в бэкап."
                                + Environment.NewLine + Environment.NewLine
                                + InstallerMetadata.DialogueHistoryNotice;
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

        private void CheckForUpdates(bool showNoUpdate)
        {
            string installedVersion = GetInstalledTranslationVersion();
            string packageVersion = InstallerMetadata.Version;
            string comparisonVersion = packageVersion;
            if (!string.IsNullOrEmpty(installedVersion)
                && UpdateChecker.IsNewerVersion(installedVersion, comparisonVersion))
            {
                comparisonVersion = installedVersion;
            }

            string installedLabel = string.IsNullOrEmpty(installedVersion) ? "не установлен" : installedVersion;
            updateButton.Enabled = false;
            Log("Проверка обновлений... Установлено: " + installedLabel + "; пакет установщика: " + packageVersion);

            Task.Factory.StartNew(delegate
            {
                return UpdateChecker.Check(comparisonVersion);
            }).ContinueWith(delegate(Task<UpdateInfo> task)
            {
                BeginInvoke((Action)delegate
                {
                    updateButton.Enabled = true;
                    if (task.Exception != null)
                    {
                        Exception ex = task.Exception.GetBaseException();
                        Log("Не удалось проверить обновления: " + ex.Message);
                        if (showNoUpdate)
                        {
                            MessageBox.Show(this, "Не удалось проверить обновления:\n" + ex.Message, "Обновления", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        }
                        return;
                    }

                    UpdateInfo info = task.Result;
                    if (info == null)
                    {
                        bool packageCanUpdateInstalled = string.IsNullOrEmpty(installedVersion)
                            || UpdateChecker.IsNewerVersion(packageVersion, installedVersion);
                        if (packageCanUpdateInstalled)
                        {
                            Log("Версия " + packageVersion + " уже доступна в этом установщике; скачивание не требуется.");
                            if (showNoUpdate)
                            {
                                MessageBox.Show(
                                    this,
                                    "В этом установщике уже есть версия перевода " + packageVersion
                                        + ".\nУстановленная версия: " + installedLabel
                                        + ".\n\nДополнительное скачивание не требуется. Нажмите «Установить перевод».",
                                    "Обновление уже в установщике",
                                    MessageBoxButtons.OK,
                                    MessageBoxIcon.Information);
                            }
                        }
                        else
                        {
                            Log("Установлена актуальная версия перевода.");
                            if (showNoUpdate)
                            {
                                MessageBox.Show(this, "Установлена актуальная версия перевода.", "Обновления", MessageBoxButtons.OK, MessageBoxIcon.Information);
                            }
                        }
                        return;
                    }

                    Log("Доступна новая версия: " + info.Version);
                    string action = info.IsPayloadPackage
                        ? "Скачать и установить свежий пакет перевода?"
                        : "Скачать и запустить новый установщик?";
                    DialogResult result = MessageBox.Show(
                        this,
                        "Доступна новая версия перевода: " + info.Version
                            + "\nУстановленная версия: " + installedLabel
                            + "\nВерсия пакета в этом установщике: " + packageVersion
                            + "\n\n" + action,
                        "Доступно обновление",
                        MessageBoxButtons.YesNo,
                        MessageBoxIcon.Information);
                    if (result == DialogResult.Yes)
                    {
                        DownloadAndLaunchUpdate(info);
                    }
                });
            });
        }

        private string GetInstalledTranslationVersion()
        {
            string dir = pathTextBox.Text.Trim();
            if (!string.IsNullOrEmpty(dir) && Directory.Exists(dir))
            {
                string installedVersion = core.GetInstalledVersion(dir);
                if (!string.IsNullOrEmpty(installedVersion))
                {
                    return installedVersion;
                }
            }

            return null;
        }

        private void DownloadAndLaunchUpdate(UpdateInfo info)
        {
            if (string.IsNullOrEmpty(info.DownloadUrl))
            {
                Process.Start(info.ReleaseUrl);
                return;
            }

            string dir = pathTextBox.Text.Trim();
            if (info.IsPayloadPackage && (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)))
            {
                MessageBox.Show(this, "Для установки обновления выберите папку игры.", "Нужна папка игры", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            SetBusy(true);
            Log("Скачивание обновления: " + info.AssetName);
            Task.Factory.StartNew(delegate
            {
                string downloaded = UpdateChecker.DownloadAsset(info, LogFromWorker);
                if (info.IsPayloadPackage)
                {
                    core.InstallFromPayloadPackage(dir, downloaded, LogFromWorker);
                }
                return downloaded;
            }).ContinueWith(delegate(Task<string> task)
            {
                BeginInvoke((Action)delegate
                {
                    SetBusy(false);
                    if (task.Exception != null)
                    {
                        Exception ex = task.Exception.GetBaseException();
                        Log("Не удалось скачать обновление: " + ex.Message);
                        MessageBox.Show(this, "Не удалось скачать обновление:\n" + ex.Message, "Обновления", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    }

                    string downloaded = task.Result;
                    if (info.IsPayloadPackage)
                    {
                        Log("Обновление установлено из пакета: " + downloaded);
                        MessageBox.Show(
                            this,
                            "Свежая версия перевода установлена. Оригинальные файлы сохранены в бэкап."
                                + Environment.NewLine + Environment.NewLine
                                + InstallerMetadata.DialogueHistoryNotice,
                            "Обновления",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information);
                    }
                    else
                    {
                        Log("Обновление скачано: " + downloaded);
                        MessageBox.Show(this, "Новый установщик скачан и сейчас будет запущен.", "Обновления", MessageBoxButtons.OK, MessageBoxIcon.Information);
                        Process.Start(downloaded);
                        Close();
                    }
                });
            });
        }

        private void SetBusy(bool busy)
        {
            browseButton.Enabled = !busy;
            detectButton.Enabled = !busy;
            installButton.Enabled = !busy;
            restoreButton.Enabled = !busy;
            backupsButton.Enabled = !busy;
            updateButton.Enabled = !busy;
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

    internal static class InstallerMetadata
    {
        public const string RepositoryOwner = "AceAsket";
        public const string RepositoryName = "Digimon-Story-Time-Stranger-RU";
        public const string LatestReleaseApiUrl = "https://api.github.com/repos/AceAsket/Digimon-Story-Time-Stranger-RU/releases/latest";
        public const string DialogueHistoryNotice = "Важно: «История диалогов» хранит в сохранении текст уже показанных реплик. Установка или обновление перевода не меняет старые записи; новые и повторно показанные реплики отображаются в актуальной редакции.";

        public static string Version
        {
            get
            {
                using (Stream stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("DstsRuInstaller.version.txt"))
                {
                    if (stream == null)
                    {
                        return "dev";
                    }

                    using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                    {
                        string value = reader.ReadToEnd().Trim();
                        return string.IsNullOrEmpty(value) ? "dev" : value;
                    }
                }
            }
        }
    }

    internal sealed class UpdateInfo
    {
        public readonly string Version;
        public readonly string ReleaseUrl;
        public readonly string DownloadUrl;
        public readonly string AssetName;
        public readonly bool IsPayloadPackage;

        public UpdateInfo(string version, string releaseUrl, string downloadUrl, string assetName, bool isPayloadPackage)
        {
            Version = version;
            ReleaseUrl = releaseUrl;
            DownloadUrl = downloadUrl;
            AssetName = assetName;
            IsPayloadPackage = isPayloadPackage;
        }
    }

    internal sealed class UpdateAsset
    {
        public readonly string DownloadUrl;
        public readonly string AssetName;
        public readonly bool IsPayloadPackage;

        public UpdateAsset(string downloadUrl, string assetName, bool isPayloadPackage)
        {
            DownloadUrl = downloadUrl;
            AssetName = assetName;
            IsPayloadPackage = isPayloadPackage;
        }
    }

    internal static class UpdateChecker
    {
        public static UpdateInfo Check(string currentVersion)
        {
            string json = ReadUrl(InstallerMetadata.LatestReleaseApiUrl);
            string tag = JsonString(json, "tag_name");
            string releaseUrl = JsonString(json, "html_url");
            if (string.IsNullOrEmpty(tag) || !IsNewerVersion(tag, currentVersion))
            {
                return null;
            }

            UpdateAsset asset = FindUpdateAsset(json);
            if (asset == null)
            {
                return new UpdateInfo(NormalizeVersionText(tag), releaseUrl, null, "страница релиза", false);
            }
            return new UpdateInfo(NormalizeVersionText(tag), releaseUrl, asset.DownloadUrl, asset.AssetName, asset.IsPayloadPackage);
        }

        public static string DownloadAsset(UpdateInfo info, Action<string> log)
        {
            string fileName = FileNameFromUrl(info.DownloadUrl);
            if (string.IsNullOrEmpty(fileName))
            {
                fileName = info.IsPayloadPackage
                    ? "DSTS_RU_Update_" + info.Version + ".zip"
                    : "DSTS_RU_Installer_" + info.Version + ".exe";
            }

            string target = Path.Combine(Path.GetTempPath(), fileName);
            if (File.Exists(target))
            {
                File.Delete(target);
            }

            using (WebClient client = CreateWebClient())
            {
                Log(log, "Загрузка: " + info.DownloadUrl);
                client.DownloadFile(info.DownloadUrl, target);
            }

            return target;
        }

        private static string ReadUrl(string url)
        {
            ServicePointManager.SecurityProtocol = ServicePointManager.SecurityProtocol | (SecurityProtocolType)3072;
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
            request.UserAgent = "DSTS-RU-Installer/" + InstallerMetadata.Version;
            request.Accept = "application/vnd.github+json";
            request.Timeout = 10000;
            request.ReadWriteTimeout = 10000;

            try
            {
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                using (Stream stream = response.GetResponseStream())
                using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                {
                    return reader.ReadToEnd();
                }
            }
            catch (WebException ex)
            {
                HttpWebResponse response = ex.Response as HttpWebResponse;
                if (response != null && response.StatusCode == HttpStatusCode.NotFound)
                {
                    return "{}";
                }
                throw;
            }
        }

        private static WebClient CreateWebClient()
        {
            ServicePointManager.SecurityProtocol = ServicePointManager.SecurityProtocol | (SecurityProtocolType)3072;
            WebClient client = new WebClient();
            client.Headers[HttpRequestHeader.UserAgent] = "DSTS-RU-Installer/" + InstallerMetadata.Version;
            client.Headers[HttpRequestHeader.Accept] = "application/octet-stream";
            return client;
        }

        private static UpdateAsset FindUpdateAsset(string json)
        {
            MatchCollection matches = Regex.Matches(json, "\"browser_download_url\"\\s*:\\s*\"([^\"]+)\"", RegexOptions.IgnoreCase);
            UpdateAsset installerFallback = null;
            UpdateAsset exeFallback = null;
            foreach (Match match in matches)
            {
                string url = JsonUnescape(match.Groups[1].Value);
                string file = FileNameFromUrl(url);
                if (file.EndsWith(".zip", StringComparison.OrdinalIgnoreCase)
                    && (file.IndexOf("Payload", StringComparison.OrdinalIgnoreCase) >= 0
                        || file.IndexOf("Update", StringComparison.OrdinalIgnoreCase) >= 0))
                {
                    return new UpdateAsset(url, file, true);
                }

                if (file.EndsWith(".exe", StringComparison.OrdinalIgnoreCase))
                {
                    if (file.IndexOf("DSTS_RU_Installer", StringComparison.OrdinalIgnoreCase) >= 0
                        || file.IndexOf("DSTS-RU-Installer", StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        installerFallback = new UpdateAsset(url, file, false);
                    }
                    exeFallback = exeFallback ?? new UpdateAsset(url, file, false);
                }
            }
            return installerFallback ?? exeFallback;
        }

        public static bool IsNewerVersion(string remote, string current)
        {
            Version remoteVersion;
            Version currentVersion;
            if (!Version.TryParse(NormalizeVersionText(remote), out remoteVersion)
                || !Version.TryParse(NormalizeVersionText(current), out currentVersion))
            {
                return false;
            }
            return remoteVersion.CompareTo(currentVersion) > 0;
        }

        private static string NormalizeVersionText(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return "";
            }

            Match match = Regex.Match(value, "\\d+(?:\\.\\d+){0,3}");
            return match.Success ? match.Value : value.Trim().TrimStart('v', 'V');
        }

        private static string JsonString(string json, string name)
        {
            Match match = Regex.Match(json, "\"" + Regex.Escape(name) + "\"\\s*:\\s*\"([^\"]*)\"", RegexOptions.IgnoreCase);
            return match.Success ? JsonUnescape(match.Groups[1].Value) : null;
        }

        private static string JsonUnescape(string value)
        {
            if (value == null)
            {
                return null;
            }

            string result = value.Replace("\\/", "/").Replace("\\\"", "\"").Replace("\\\\", "\\");
            return Regex.Replace(result, "\\\\u([0-9a-fA-F]{4})", delegate(Match match)
            {
                int code = Convert.ToInt32(match.Groups[1].Value, 16);
                return ((char)code).ToString();
            });
        }

        private static string FileNameFromUrl(string url)
        {
            try
            {
                return Path.GetFileName(new Uri(url).LocalPath);
            }
            catch
            {
                return "";
            }
        }

        private static void Log(Action<string> log, string message)
        {
            if (log != null)
            {
                log(message);
            }
        }
    }

    internal sealed class InstallerCore
    {
        private static readonly string[] RequiredGameDataPayloadFiles = new[]
        {
            "app_text01.dx11.mvgl",
            "patch_text01.dx11.mvgl"
        };

        private static readonly string[] RequiredRootPayloadFiles = new[]
        {
            "dinput8.dll"
        };

        private static readonly string[] GameExecutableNames = new[]
        {
            "Digimon Story Time Stranger.exe",
            "Digimon Story Time Stranger Demo.exe"
        };

        private static readonly string[] RequiredPayloadFiles =
            RequiredGameDataPayloadFiles.Concat(RequiredRootPayloadFiles).ToArray();

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

        private static readonly string[] GameDataPayloadFiles =
            RequiredGameDataPayloadFiles.Concat(OptionalPayloadFiles).ToArray();
        private const string PayloadResourcePrefix = "DstsRuPayload.";
        private const string InstalledVersionFileName = "_dsts_ru_translation_version.txt";
        private const string NativeInputMarkerFileName = "_dsts_ru_input_fix.txt";
        private const string CreatedFilesListName = "_dsts_ru_created_files.txt";

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
            if (!GameExecutableNames.Any(file => File.Exists(Path.Combine(fullRoot, file))))
            {
                throw new InvalidOperationException(
                    "В выбранной папке нет исполняемого файла Digimon Story Time Stranger. "
                    + "Выберите корневую папку игры, а не gamedata и не родительский каталог.");
            }
            foreach (string file in RequiredGameDataPayloadFiles)
            {
                FindTargetFile(fullRoot, file);
            }
        }

        public string GetInstalledVersion(string root)
        {
            try
            {
                string versionFile = Path.Combine(Path.GetFullPath(root), InstalledVersionFileName);
                if (!File.Exists(versionFile))
                {
                    return null;
                }

                string version = File.ReadAllText(versionFile, Encoding.UTF8).Trim();
                return string.IsNullOrEmpty(version) ? null : version;
            }
            catch
            {
                return null;
            }
        }

        public void Install(string root, Action<string> log)
        {
            InstallWithPayload(root, log, null);
        }

        public void InstallFromPayloadPackage(string root, string packagePath, Action<string> log)
        {
            if (string.IsNullOrEmpty(packagePath) || !File.Exists(packagePath))
            {
                throw new InvalidOperationException("Пакет обновления не найден: " + packagePath);
            }

            string tempDir = Path.Combine(Path.GetTempPath(), "dsts_ru_payload_" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(tempDir);
            try
            {
                Log(log, "Распаковка пакета обновления...");
                ZipFile.ExtractToDirectory(packagePath, tempDir);
                string payloadDir = FindPayloadDir(tempDir);
                Log(log, "Payload обновления: " + payloadDir);
                InstallWithPayload(root, log, payloadDir);
            }
            finally
            {
                try
                {
                    if (Directory.Exists(tempDir))
                    {
                        Directory.Delete(tempDir, true);
                    }
                }
                catch
                {
                }
            }
        }

        private void InstallWithPayload(string root, Action<string> log, string payloadOverrideDir)
        {
            string fullRoot = Path.GetFullPath(root);
            EnsurePayloadExists(payloadOverrideDir);
            ValidateGameDir(fullRoot);
            ValidateNativeInputPayload(fullRoot, payloadOverrideDir);

            string backupDir = Path.Combine(fullRoot, "_dsts_ru_backups", DateTime.Now.ToString("yyyyMMdd-HHmmss"));
            Directory.CreateDirectory(backupDir);

            List<ManifestEntry> entries = new List<ManifestEntry>();
            List<string> createdFiles = new List<string>();
            foreach (string file in GameDataPayloadFiles)
            {
                bool optional = OptionalPayloadFiles.Contains(file);
                if (optional && !HasPayloadFile(file, payloadOverrideDir))
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
                CopyPayloadFile(file, target, payloadOverrideDir);

                entries.Add(new ManifestEntry(relative, backupFile));
            }

            string installedVersion = ResolvePayloadVersion(payloadOverrideDir);
            foreach (string file in RequiredRootPayloadFiles)
            {
                string target = Path.Combine(fullRoot, file);
                BackupOrRecordCreated(fullRoot, backupDir, target, entries, createdFiles, log);
                Log(log, "Установка: " + file);
                CopyPayloadFile(file, target, payloadOverrideDir);
            }

            string nativeMarker = Path.Combine(fullRoot, NativeInputMarkerFileName);
            BackupOrRecordCreated(fullRoot, backupDir, nativeMarker, entries, createdFiles, log);
            string nativeHash = ComputePayloadHash(RequiredRootPayloadFiles[0], payloadOverrideDir);
            File.WriteAllText(
                nativeMarker,
                "version=" + installedVersion + Environment.NewLine
                    + "sha256=" + nativeHash + Environment.NewLine,
                new UTF8Encoding(false));

            if (createdFiles.Count > 0)
            {
                File.WriteAllLines(
                    Path.Combine(backupDir, CreatedFilesListName),
                    createdFiles,
                    new UTF8Encoding(false));
            }
            File.WriteAllText(
                Path.Combine(backupDir, "manifest.json"),
                BuildManifest(fullRoot, entries, createdFiles),
                new UTF8Encoding(false));
            WriteInstalledVersion(fullRoot, installedVersion);
            Log(log, "Версия перевода: " + installedVersion);
            Log(log, "Исправление ввода кириллического имени установлено.");
            Log(log, InstallerMetadata.DialogueHistoryNotice);
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

            string createdListPath = Path.Combine(latest.FullName, CreatedFilesListName);
            List<string> createdFiles = File.Exists(createdListPath)
                ? File.ReadAllLines(createdListPath, Encoding.UTF8)
                    .Where(line => !string.IsNullOrWhiteSpace(line))
                    .ToList()
                : new List<string>();

            foreach (FileInfo file in EnumerateFilesSafe(latest.FullName, "*"))
            {
                if (string.Equals(file.Name, "manifest.json", StringComparison.OrdinalIgnoreCase)
                    || string.Equals(file.Name, CreatedFilesListName, StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                string relative = GetRelativePath(latest.FullName, file.FullName);
                string target = Path.Combine(fullRoot, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(target));
                Log(log, "Восстановление: " + relative);
                File.Copy(file.FullName, target, true);
            }

            foreach (string relative in createdFiles)
            {
                string target = SafePathBelowRoot(fullRoot, relative);
                if (File.Exists(target))
                {
                    Log(log, "Удаление добавленного файла: " + relative);
                    File.Delete(target);
                }
            }

            ClearInstalledVersion(fullRoot);
            Log(log, "Восстановлен бэкап: " + latest.FullName);
        }

        private void ValidateNativeInputPayload(string root, string payloadOverrideDir)
        {
            string target = Path.Combine(root, RequiredRootPayloadFiles[0]);
            if (!File.Exists(target))
            {
                return;
            }

            string targetHash = ComputeFileHash(target);
            string payloadHash = ComputePayloadHash(RequiredRootPayloadFiles[0], payloadOverrideDir);
            if (string.Equals(targetHash, payloadHash, StringComparison.OrdinalIgnoreCase))
            {
                return;
            }

            string marker = Path.Combine(root, NativeInputMarkerFileName);
            string recordedHash = null;
            if (File.Exists(marker))
            {
                foreach (string line in File.ReadAllLines(marker, Encoding.UTF8))
                {
                    if (line.StartsWith("sha256=", StringComparison.OrdinalIgnoreCase))
                    {
                        recordedHash = line.Substring("sha256=".Length).Trim();
                        break;
                    }
                }
            }

            if (!string.IsNullOrEmpty(recordedHash)
                && string.Equals(targetHash, recordedHash, StringComparison.OrdinalIgnoreCase))
            {
                return;
            }

            throw new InvalidOperationException(
                "В папке игры уже есть сторонний dinput8.dll. Установщик не будет его перезаписывать. "
                + "Удалите конфликтующий мод вручную или восстановите его штатным способом, затем повторите установку.");
        }

        private static void BackupOrRecordCreated(
            string root,
            string backupDir,
            string target,
            List<ManifestEntry> entries,
            List<string> createdFiles,
            Action<string> log)
        {
            string relative = GetRelativePath(root, target);
            if (!File.Exists(target))
            {
                createdFiles.Add(relative);
                return;
            }

            string backupFile = Path.Combine(backupDir, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(backupFile));
            Log(log, "Бэкап: " + relative);
            File.Copy(target, backupFile, true);
            entries.Add(new ManifestEntry(relative, backupFile));
        }

        private string ComputePayloadHash(string file, string payloadOverrideDir)
        {
            if (!string.IsNullOrEmpty(payloadOverrideDir))
            {
                return ComputeFileHash(Path.Combine(payloadOverrideDir, file));
            }

            if (HasEmbeddedPayload)
            {
                string resourceName = PayloadResourcePrefix + file;
                using (Stream input = Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName))
                {
                    if (input == null)
                    {
                        throw new InvalidOperationException("Во встроенном payload не найден файл: " + file);
                    }
                    return ComputeStreamHash(input);
                }
            }

            return ComputeFileHash(Path.Combine(PayloadDir, file));
        }

        private static string ComputeFileHash(string path)
        {
            using (FileStream input = File.OpenRead(path))
            {
                return ComputeStreamHash(input);
            }
        }

        private static string ComputeStreamHash(Stream input)
        {
            using (SHA256 sha256 = SHA256.Create())
            {
                return BitConverter.ToString(sha256.ComputeHash(input)).Replace("-", "").ToLowerInvariant();
            }
        }

        private static string SafePathBelowRoot(string root, string relative)
        {
            string fullRoot = Path.GetFullPath(root)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;
            string candidate = Path.GetFullPath(Path.Combine(fullRoot, relative));
            if (!candidate.StartsWith(fullRoot, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Небезопасный путь в списке восстановления: " + relative);
            }
            return candidate;
        }

        private void EnsurePayloadExists(string payloadOverrideDir = null)
        {
            if (!string.IsNullOrEmpty(payloadOverrideDir))
            {
                if (!Directory.Exists(payloadOverrideDir))
                {
                    throw new InvalidOperationException("Папка payload не найдена: " + payloadOverrideDir);
                }
                foreach (string file in RequiredPayloadFiles)
                {
                    string payloadFile = Path.Combine(payloadOverrideDir, file);
                    if (!File.Exists(payloadFile))
                    {
                        throw new InvalidOperationException("В payload обновления не найден файл: " + payloadFile);
                    }
                }
                return;
            }

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

        private bool HasPayloadFile(string file, string payloadOverrideDir = null)
        {
            if (!string.IsNullOrEmpty(payloadOverrideDir))
            {
                return File.Exists(Path.Combine(payloadOverrideDir, file));
            }
            if (HasEmbeddedPayload)
            {
                return embeddedPayloadFiles.Contains(file);
            }
            return File.Exists(Path.Combine(PayloadDir, file));
        }

        private void CopyPayloadFile(string file, string target, string payloadOverrideDir = null)
        {
            if (!string.IsNullOrEmpty(payloadOverrideDir))
            {
                File.Copy(Path.Combine(payloadOverrideDir, file), target, true);
                return;
            }

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

        private string ResolvePayloadVersion(string payloadOverrideDir)
        {
            if (!string.IsNullOrEmpty(payloadOverrideDir))
            {
                List<string> candidates = new List<string>();
                candidates.Add(Path.Combine(payloadOverrideDir, "VERSION"));

                DirectoryInfo parent = Directory.GetParent(payloadOverrideDir);
                if (parent != null)
                {
                    candidates.Add(Path.Combine(parent.FullName, "VERSION"));
                }

                foreach (string candidate in candidates)
                {
                    if (File.Exists(candidate))
                    {
                        string version = File.ReadAllText(candidate, Encoding.UTF8).Trim();
                        if (!string.IsNullOrEmpty(version))
                        {
                            return version;
                        }
                    }
                }
            }

            return InstallerMetadata.Version;
        }

        private void WriteInstalledVersion(string root, string version)
        {
            string versionFile = Path.Combine(root, InstalledVersionFileName);
            File.WriteAllText(versionFile, version + Environment.NewLine, new UTF8Encoding(false));
        }

        private void ClearInstalledVersion(string root)
        {
            string versionFile = Path.Combine(root, InstalledVersionFileName);
            if (File.Exists(versionFile))
            {
                File.Delete(versionFile);
            }
        }

        private string FindPayloadDir(string unpackedRoot)
        {
            string directPayload = Path.Combine(unpackedRoot, "payload");
            if (Directory.Exists(directPayload) && RequiredPayloadFiles.All(file => File.Exists(Path.Combine(directPayload, file))))
            {
                return directPayload;
            }

            if (RequiredPayloadFiles.All(file => File.Exists(Path.Combine(unpackedRoot, file))))
            {
                return unpackedRoot;
            }

            foreach (DirectoryInfo dir in new DirectoryInfo(unpackedRoot).GetDirectories("*", SearchOption.AllDirectories))
            {
                if (RequiredPayloadFiles.All(file => File.Exists(Path.Combine(dir.FullName, file))))
                {
                    return dir.FullName;
                }
            }

            throw new InvalidOperationException("В пакете обновления не найдена папка payload с файлами перевода.");
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

        private static string BuildManifest(
            string gameDir,
            List<ManifestEntry> entries,
            List<string> createdFiles)
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
            builder.AppendLine("  ],");
            builder.AppendLine("  \"created_files\": [");
            for (int i = 0; i < createdFiles.Count; i++)
            {
                builder.Append("    \"" + JsonEscape(createdFiles[i]) + "\"");
                if (i + 1 < createdFiles.Count)
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

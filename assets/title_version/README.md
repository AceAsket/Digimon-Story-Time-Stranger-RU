# Title-screen translation version

`ui_title_copyright_01.img` is the release asset injected into the existing
`app_text01/images/ui_title_copyright_01.img` entry. It adds the unobtrusive
`DSTS RU v<version>` label to the left of the original copyright line.

The asset remains a 2048 x 32, one-mip `BC7_UNORM` DDS. The generator restores
the original DDS header and every BC7 block outside the reserved label area, so
the official copyright artwork stays byte-for-byte unchanged.

When `VERSION` changes, regenerate the asset explicitly:

```powershell
$env:TEXCONV_EXE = "C:\path\to\DirectXTex\texconv.exe"
python scripts/update_title_version_asset.py
```

The normal release build does not recompress this texture. It compares
`assets/title_version/VERSION` with the repository `VERSION`, injects the
committed `.img`, and verifies the packed archive hash and DDS metadata.

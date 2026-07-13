# MVGLTools v2.2.0 local pack fix

`MVGLTools-v2.2.0-bounded-packer.patch` fixes the upstream Windows packer
hang/race encountered while rebuilding DSTS archives.

Apply it to the upstream `v2.2.0` source tree:

```powershell
git apply --unidiff-zero D:\digimon\tools\patches\MVGLTools-v2.2.0-bounded-packer.patch
```

The fix captures worker inputs by value, propagates compression exceptions and
keeps at most four compression jobs in flight. The additional `ws2_32` link is
required for the local MinGW build.

Validation performed for this project:

- `patch_text01`: 194 files, pack/unpack and SHA-256 comparison — 0 mismatches;
- full `patch`: 15,734 files / 4,404,602,735 bytes, pack/unpack and SHA-256
  comparison — 0 mismatches.

The locally built runtime is expected at
`.tools/MVGLTools-v2.2.0-fixed/MVGLToolsCLI.exe`; the DLLs produced alongside
it must remain in the same directory.

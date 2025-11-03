# 🐙 GitHub Setup Guide - Step by Step

## 📋 Pilih Metode Setup

### **Metode 1: OTOMATIS (Recommended)** ⚡
Gunakan script otomatis yang sudah disediakan

### **Metode 2: MANUAL** 🔧
Ikuti langkah manual step-by-step

---

# ⚡ METODE 1: SETUP OTOMATIS (TERCEPAT)

## A. Untuk Mac/Linux Users

### 1. Download Project
Download project dari link yang diberikan dan extract ke folder di komputer Anda.

### 2. Buka Terminal
```bash
# Masuk ke folder project
cd ~/Downloads/crypto-analyzer-improved
# Atau sesuaikan dengan lokasi folder Anda
```

### 3. Jalankan Script
```bash
# Buat script executable
chmod +x setup-github.sh

# Jalankan script
./setup-github.sh
```

### 4. Ikuti Instruksi di Layar
Script akan menanyakan:
- GitHub username Anda
- Nama repository (tekan Enter untuk default)
- Konfirmasi

### 5. Buat Repository di GitHub
Script akan memberi instruksi untuk:
1. Buka: https://github.com/new
2. Isi form sesuai instruksi
3. Klik "Create repository"

### 6. Masukkan Credentials
- **Username**: username GitHub Anda
- **Password**: Personal Access Token (BUKAN password GitHub!)

**Cara buat token:** https://github.com/settings/tokens/new

### 7. Done! ✅
Script akan push code Anda ke GitHub secara otomatis.

---

## B. Untuk Windows Users

### 1. Download Project
Download dan extract ke folder, misal: `C:\Users\YourName\crypto-analyzer-improved`

### 2. Buka Command Prompt
Tekan `Win + R`, ketik `cmd`, Enter

```cmd
cd C:\Users\YourName\crypto-analyzer-improved
```

### 3. Jalankan Script
```cmd
setup-github.bat
```

### 4-7. Sama seperti Mac/Linux
Ikuti instruksi yang muncul di layar.

---

# 🔧 METODE 2: SETUP MANUAL (DETAIL)

Jika script otomatis tidak bekerja, ikuti langkah manual ini:

## Step 1: Install Git (Jika Belum Ada)

### Windows
1. Download: https://git-scm.com/download/win
2. Jalankan installer
3. Klik "Next" semua sampai selesai
4. Restart Command Prompt

### Mac
```bash
# Install Homebrew dulu (jika belum ada)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Git
brew install git
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install git
```

### Verify Installation
```bash
git --version
# Harus muncul: git version 2.x.x
```

---

## Step 2: Konfigurasi Git (First Time Only)

```bash
# Set nama Anda
git config --global user.name "Your Name"

# Set email Anda
git config --global user.email "wibiar279@gmail.com"

# Verify
git config --list
```

---

## Step 3: Buat GitHub Repository

### 3.1. Buka GitHub
Buka browser, masuk ke: https://github.com/new

### 3.2. Isi Form Repository

| Field | Value |
|-------|-------|
| **Repository name** | `crypto-analyzer-improved` |
| **Description** | `Professional crypto analyzer with improved security and features` |
| **Visibility** | **Public** (atau Private) |
| **Initialize this repository with:** | |
| ❌ Add a README file | JANGAN CENTANG |
| ❌ Add .gitignore | JANGAN CENTANG |
| ❌ Choose a license | JANGAN CENTANG |

### 3.3. Klik "Create repository"

**PENTING**: Jangan initialize dengan apa pun! Kita sudah punya file-file nya.

### 3.4. Copy Repository URL
Setelah repository dibuat, copy URL yang muncul, contoh:
```
https://github.com/wibiar279-sketch/crypto-analyzer-improved.git
```

---

## Step 4: Initialize Git di Project Anda

### 4.1. Buka Terminal/Command Prompt

**Windows:**
```cmd
cd C:\Users\YourName\crypto-analyzer-improved
```

**Mac/Linux:**
```bash
cd ~/Downloads/crypto-analyzer-improved
```

### 4.2. Initialize Git
```bash
git init
```

Output: `Initialized empty Git repository in /path/to/crypto-analyzer-improved/.git/`

---

## Step 5: Add Files ke Git

```bash
# Add semua file
git add .

# Verify files added
git status
```

Anda akan melihat daftar file yang akan di-commit (warna hijau).

---

## Step 6: Create First Commit

```bash
git commit -m "Initial commit: Improved crypto analyzer with enhanced security and features"
```

Output: `[main xxxxx] Initial commit: Improved crypto analyzer...`

---

## Step 7: Rename Branch ke 'main'

```bash
git branch -M main
```

Ini merename branch default ke 'main' (GitHub standard).

---

## Step 8: Add Remote Repository

```bash
# Ganti dengan URL repository Anda
git remote add origin https://github.com/wibiar279-sketch/crypto-analyzer-improved.git

# Verify
git remote -v
```

Output:
```
origin  https://github.com/wibiar279-sketch/crypto-analyzer-improved.git (fetch)
origin  https://github.com/wibiar279-sketch/crypto-analyzer-improved.git (push)
```

---

## Step 9: Push ke GitHub

### 9.1. Push
```bash
git push -u origin main
```

### 9.2. Enter Credentials

Anda akan diminta:

**Username for 'https://github.com':**
```
wibiar279-sketch
```

**Password for 'https://wibiar279-sketch@github.com':**
```
[PASTE YOUR PERSONAL ACCESS TOKEN HERE]
```

⚠️ **PENTING**: Jangan gunakan password GitHub! Gunakan **Personal Access Token**!

---

## Step 10: Create Personal Access Token (Jika Belum Ada)

### 10.1. Buka GitHub Settings
1. Klik foto profil (kanan atas)
2. Klik **Settings**
3. Scroll ke bawah, klik **Developer settings** (kiri bawah)
4. Klik **Personal access tokens**
5. Klik **Tokens (classic)**
6. Klik **Generate new token**
7. Klik **Generate new token (classic)**

### 10.2. Isi Form Token

| Field | Value |
|-------|-------|
| **Note** | `crypto-analyzer-deploy` |
| **Expiration** | 90 days (atau sesuai kebutuhan) |
| **Select scopes** | |
| ✅ **repo** | Centang semua (full control) |
| ✅ **workflow** | Centang (untuk GitHub Actions) |

### 10.3. Generate & Copy Token
1. Scroll ke bawah
2. Klik **Generate token**
3. **COPY TOKEN** (hijau) - Anda tidak akan melihatnya lagi!
4. Simpan di tempat aman (Notepad, dll)

### 10.4. Gunakan Token sebagai Password
Saat git push minta password, paste token ini.

---

## Step 11: Verify Upload

### 11.1. Buka Repository
Buka browser: `https://github.com/wibiar279-sketch/crypto-analyzer-improved`

### 11.2. Check Files
Anda harus melihat:
- ✅ README.md
- ✅ backend/ folder
- ✅ frontend/ folder
- ✅ docker-compose.yml
- ✅ .github/workflows/
- ✅ Dan file-file lainnya

### 11.3. Check README
Klik README.md - harus terlihat dokumentasi lengkap.

---

## ✅ SUCCESS! Code Anda Sudah di GitHub! 🎉

Repository URL:
```
https://github.com/wibiar279-sketch/crypto-analyzer-improved
```

---

# 🚨 TROUBLESHOOTING

## Problem 1: "git: command not found"

**Solusi:**
- Git belum terinstall
- Install sesuai Step 1 di atas
- Restart terminal/command prompt

---

## Problem 2: "Permission denied (publickey)"

**Solusi:**
- Gunakan HTTPS, bukan SSH
- URL harus: `https://github.com/...` bukan `git@github.com:...`

**Fix:**
```bash
git remote set-url origin https://github.com/wibiar279-sketch/crypto-analyzer-improved.git
git push -u origin main
```

---

## Problem 3: "Authentication failed"

**Penyebab:** Menggunakan password GitHub (tidak akan berfungsi lagi)

**Solusi:**
1. Buat Personal Access Token (Step 10)
2. Gunakan token sebagai password
3. Retry push

---

## Problem 4: "repository not found"

**Penyebab:**
- Repository belum dibuat di GitHub
- URL salah
- Username salah

**Solusi:**
1. Pastikan repository sudah dibuat: https://github.com/new
2. Check URL remote:
   ```bash
   git remote -v
   ```
3. Jika salah, update:
   ```bash
   git remote set-url origin https://github.com/USERNAME/REPO_NAME.git
   ```

---

## Problem 5: "failed to push some refs"

**Penyebab:** Remote repository punya commits yang belum ada di local

**Solusi:**
```bash
# Pull dulu
git pull origin main --allow-unrelated-histories

# Resolve conflicts (jika ada)
git add .
git commit -m "Merge remote changes"

# Push lagi
git push -u origin main
```

---

## Problem 6: "Support for password authentication was removed"

**Solusi:**
Ini pesan standar. **Gunakan Personal Access Token**, bukan password!

---

## Problem 7: Token Tidak Berfungsi

**Checklist:**
1. ✅ Token sudah copied dengan benar (no extra spaces)?
2. ✅ Token punya scope 'repo' dan 'workflow'?
3. ✅ Token belum expired?
4. ✅ Paste sebagai password, bukan di field username?

**Generate token baru jika perlu:**
https://github.com/settings/tokens/new

---

# 📞 Masih Ada Masalah?

## Option 1: GitHub Desktop (GUI - Paling Mudah!)

1. Download: https://desktop.github.com/
2. Install & login
3. File → Add Local Repository → Pilih folder project
4. Klik "Publish repository"
5. Done!

## Option 2: VS Code Git Integration

1. Buka VS Code
2. Open folder project
3. Source Control panel (kiri)
4. Initialize Repository
5. Commit changes
6. Publish to GitHub

## Option 3: Manual via Web

1. Buat ZIP dari folder project
2. Upload ke https://github.com/new
3. Drag & drop ZIP file

---

# 🎓 Git Commands Reference

Untuk ke depannya:

```bash
# Check status
git status

# Add files
git add .
git add filename.txt

# Commit
git commit -m "Your message"

# Push
git push

# Pull (update dari remote)
git pull

# View history
git log
git log --oneline

# Create branch
git checkout -b feature-name

# Switch branch
git checkout main

# Merge branch
git merge feature-name

# Undo changes
git reset --hard HEAD

# View remotes
git remote -v
```

---

# 📚 Helpful Resources

- **Git Official Docs**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **Learn Git Branching**: https://learngitbranching.js.org/

---

# ✅ Next Steps After GitHub Upload

1. ✅ **Read README.md** on your repository
2. ✅ **Follow DEPLOYMENT.md** to deploy
3. ✅ **Test locally** with Docker
4. ✅ **Deploy to production** (Railway/Heroku)
5. ✅ **Set up CI/CD** (Already configured!)

---

**Selamat! Code Anda sekarang di GitHub! 🎉**

Repository: https://github.com/wibiar279-sketch/crypto-analyzer-improved

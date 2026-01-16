# Medha AI - APK Build Kaise Kare

## 📱 Option 1: GitHub Actions (RECOMMENDED - Automatic Cloud Build)

### Setup (5 minutes):

1. **GitHub Account Banao** (agar nahi hai)
   - https://github.com → Sign up

2. **Repository Banao**
   ```
   - New repository
   - Name: medha-ai-mobile
   - Public (ya Private)
   - Create
   ```

3. **Code Upload Karo**
   ```powershell
   cd "D:\apps\ai assistant medha"
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/medha-ai-mobile.git
   git push -u origin main
   ```

4. **APK Build Hoga Automatically!**
   - GitHub → Your Repo → Actions tab
   - "Build Android APK" workflow
   - 10-15 minutes me APK ready
   - Download from Artifacts

### ✅ Ye Sabse Easy Hai!

---

## 📱 Option 2: WSL (Windows Subsystem for Linux)

### Setup (20-30 minutes):

1. **WSL Install Karo**
   ```powershell
   wsl --install Ubuntu
   # Restart computer
   ```

2. **WSL Me Jaao**
   ```powershell
   wsl
   ```

3. **Dependencies Install Karo**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip git zip unzip openjdk-17-jdk
   sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
   sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
   pip3 install buildozer cython==0.29.33
   ```

4. **Project Copy Karo**
   ```bash
   cp -r /mnt/d/apps/ai\ assistant\ medha /home/YOUR_USERNAME/medha-ai
   cd /home/YOUR_USERNAME/medha-ai
   ```

5. **APK Build Karo**
   ```bash
   buildozer android debug
   # First time: 20-30 minutes (downloads Android SDK ~1GB)
   # Output: bin/medhaai-1.0-debug.apk
   ```

---

## 📱 Option 3: Android Studio (Manual Build)

1. Android Studio install karo
2. Empty Activity project banao
3. WebView add karo jo Python backend ko call kare
4. APK export karo

**Time:** 1-2 hours
**Complexity:** Medium

---

## 🎯 Meri Recommendation:

### **OPTION 1 USE KARO (GitHub Actions)**

**Kyun?**
- ✅ No local setup needed
- ✅ Automatic builds
- ✅ Free for public repos
- ✅ 10-15 minutes me ready
- ✅ Sabse easy!

### Next Steps:

1. Mujhe batao GitHub account hai?
2. Main guide karunga step-by-step
3. 10 minutes me APK ready!

**Ya WSL prefer karte ho?**

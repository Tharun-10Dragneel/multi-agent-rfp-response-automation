# Cross-Platform Frontend Setup Guide

## 🚀 Quick Start (Recommended)

### For macOS/Linux Users:
```bash
cd frontend
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### For Windows Users:
```cmd
cd frontend
scripts\setup.bat
```

## 🔧 Manual Setup (if scripts fail)

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation Steps

1. **Clean existing dependencies** (important for platform switching):
```bash
rm -rf node_modules package-lock.json  # macOS/Linux
# OR
rmdir /s /q node_modules & del package-lock.json  # Windows
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

## 🐛 Common Issues & Solutions

### Issue: "No such file or directory" for Darwin binaries
**Cause:** Platform-specific binaries missing for your OS
**Solution:** The updated package.json includes cross-platform binaries. Run `npm install`.

### Issue: Tailwind CSS not working
**Cause:** Missing or incorrect Tailwind configuration
**Solution:** 
- Ensure `tailwind.config.ts` exists
- Check `postcss.config.mjs` is correct
- Restart dev server after config changes

### Issue: Styles not loading on login page
**Cause:** CSS variables not defined or Tailwind not processing
**Solution:**
1. Check browser console for CSS errors
2. Verify `app/globals.css` is being imported
3. Run `npm run dev` with clean cache: `npm run dev -- --reset-cache`

### Issue: Module not found errors
**Cause:** Dependency installation incomplete
**Solution:**
```bash
npm install --force
# OR
npm ci
```

## 🖥️ Platform-Specific Notes

### macOS (Apple Silicon)
- ✅ Fully supported
- Uses `@next/swc-darwin-arm64` binaries

### macOS (Intel)
- ✅ Fully supported  
- Uses `@next/swc-darwin-x64` binaries

### Windows (x64)
- ✅ Fully supported
- Uses `@next/swc-win32-x64` binaries

### Windows (ARM)
- ✅ Supported
- Uses `@next/swc-win32-arm64` binaries

### Linux (x64/ARM)
- ✅ Supported
- Uses appropriate Linux binaries

## 🔍 Debugging Steps

If you encounter issues:

1. **Check Node version**: `node --version` (should be 18+)
2. **Clear npm cache**: `npm cache clean --force`
3. **Delete node_modules**: `rm -rf node_modules`
4. **Reinstall**: `npm install`
5. **Check for errors**: `npm run dev 2>&1 | tee dev.log`

## 📱 Testing

After setup, verify:
1. Development server starts: `npm run dev`
2. Login page loads at `http://localhost:3000/login`
3. Styles are applied (check dark theme, gradients, etc.)
4. Demo credentials work: `john@example.com / Password123`

## 🆘 Still Having Issues?

1. Check the specific error in browser console (F12)
2. Look at terminal output for build errors
3. Ensure all dependencies installed: `npm list --depth=0`
4. Try a different browser (Chrome, Firefox, Safari)

## 📝 Additional Notes

- The project uses Next.js 16 with React 19
- Tailwind CSS v4 with custom design system
- shadcn/ui components for consistent UI
- Demo authentication system (no backend required for UI testing)

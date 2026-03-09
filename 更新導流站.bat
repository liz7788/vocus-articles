@echo off
chcp 65001 >nul
echo === 更新方格子 SEO 導流站 ===
echo.

cd /d "%~dp0"

:: 重新生成頁面
python -X utf8 generate_site.py

:: 推上 GitHub
git add .
git commit -m "Update articles"
git push

echo.
echo === 更新完成！GitHub Pages 會在 1-2 分鐘後自動部署 ===
echo 網站：https://liz08210818-code.github.io/vocus-articles/
pause

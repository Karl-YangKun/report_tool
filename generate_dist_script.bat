@echo off
chcp 65001 > nul
echo 这是一个测试字符串

cp config.json dist/config.json
cp database.json dist/database.json
cp database.accdb dist/database.accdb
cp report.xlsx dist/report.xlsx
cp version dist/version
cp "使用文档.docx" "dist/使用文档.docx"

:: 定义文件路径和压缩工具路径
set filename="version"
:: 如果没有添加到PATH，请使用完整路径
set zip_path="C:\Program Files\7-Zip\7z.exe"

set folder_to_compress=dist

:: 使用 for /f 循环读取文件的第一行
for /f "usebackq delims=" %%a in (%filename%) do (
    set version=%%a
    goto :breakloop
)
 
:breakloop
echo 打包版本: %version%


:: 检查文件夹是否存在
if not exist "%folder_to_compress%" (
    echo 文件夹 "%folder_to_compress%" 不存在！
    exit /b 1
)

:: 定义压缩文件名（可以根据需要修改）
set archive_name=%folder_to_compress%_%version%.zip

:: 使用7-Zip进行压缩
%zip_path% a -tzip %archive_name% %folder_to_compress%

if %errorlevel% equ 0 (
    echo 文件夹 "%folder_to_compress%" 已成功压缩为 "%archive_name%"
) else (
    echo 压缩失败，错误代码：%errorlevel%
)

pause

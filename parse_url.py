import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path

def clean_text(text):
    """清理文本，去除多余空白字符"""
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_text_bs4_lxml(html_content):
    """使用BeautifulSoup和lxml解析器提取文本"""
    # 确保html_content是字符串类型
    if isinstance(html_content, bytes):
        html_content = html_content.decode('utf-8', errors='replace')
        
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 删除脚本和样式元素
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    
    # 获取正文
    text = soup.get_text()
    return clean_text(text)

def parse_url(url):
    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果请求不成功则抛出异常
        
        # 获取HTML内容
        html_content = response.content
        
        # 解析HTML并提取文本
        extracted_text = extract_text_bs4_lxml(html_content)
        
        # 提取网页名称作为文件名
        soup = BeautifulSoup(html_content.decode('utf-8', errors='replace'), 'lxml')
        title = soup.title.string if soup.title else None
        if title:
            # 清理标题，移除非法字符
            title = "".join(c for c in title if c.isalnum() or c in ' _-').strip()
            title = title.replace(' ', '_')[:100]  # 限制长度
        else:
            # 使用URL的路径部分作为文件名
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            title = os.path.basename(path) if path and path != '/' else parsed_url.netloc
            
        if not title:
            title = "webpage"
        
        # 创建outputs文件夹（如果不存在）
        output_dir = Path('./outputs')
        output_dir.mkdir(exist_ok=True)
        
        # 保存提取的文本
        output_file = output_dir / f"{title}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        print(f"已成功解析URL: {url}")
        print(f"结果保存到: {output_file}")
        return True
    
    except Exception as e:
        print(f"解析URL时出错: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈，便于调试
        return False

def main():
    print("HTML文件解析工具 (bs4-lxml方案)")
    print("=" * 50)
    print("请输入要解析的URL:")
    
    url = input("> ").strip()
    
    if not url:
        print("URL不能为空，程序退出")
        return
        
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
        print(f"已添加https://前缀: {url}")
    
    parse_url(url)
    print("解析完成，程序退出")

if __name__ == "__main__":
    main()
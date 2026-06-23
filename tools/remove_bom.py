import sys
import codecs

def remove_bom(path):
    with open(path, 'rb') as f:
        b = f.read()
    try:
        text = codecs.decode(b, 'utf-8-sig')
    except Exception:
        # fallback: try latin-1
        text = b.decode('latin-1')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('rewritten without BOM:', path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: remove_bom.py <path>')
        sys.exit(1)
    remove_bom(sys.argv[1])

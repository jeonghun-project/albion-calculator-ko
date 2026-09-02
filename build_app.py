import json, os
tpl = open('app_template.html', encoding='utf-8').read()
data = open('albion_data.json', encoding='utf-8').read()
data = data.replace('<', '\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
out = tpl.replace('__ALBION_DATA__', data)
open('index.html','w',encoding='utf-8').write(out)
print('빌드 완료 (index.html):', round(os.path.getsize('index.html')/1024/1024,2), 'MB')

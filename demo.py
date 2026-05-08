import json
import ttsfrd

resource_dir = '/app/resource'

frd = ttsfrd.TtsFrontendEngine()
frd.initialize(resource_dir)
frd.set_lang_type('pinyinvg')

text = "您好，欢迎致电合力亿捷，您在深圳市福田区人民法院的（2026）粤0307民初2394号知识产权纠纷案件，已依法向您预留的邮箱982145926@qq.com送达相关法律文书。您的身份证号后四位是1301。法院位置是朝南出发，经过银行后步行100米。价格是1988元。您看还有什么问题？欢迎和我沟通，我随时为您服务，再见。"
texts = [i["text"] for i in json.loads(frd.do_voicegen_frd(text))["sentences"]]
text = ''.join(texts)
print(text)
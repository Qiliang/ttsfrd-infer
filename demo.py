import json
import ttsfrd

resource_dir = 'cosyvoice-ttsfrd/resource'

frd = ttsfrd.TtsFrontendEngine()
frd.initialize(resource_dir)
# pinyin — 基础拼音
# pinyinfp — 拼音 FP（Fine-grained Phoneme）
# pinyinvg — 拼音 VG（当前项目使用的，适用于 CosyVoice）
# pinyinvgml — 拼音 VG Multi-Language
frd.set_lang_type('pinyinvg')

text = "您好，欢迎致电合力亿捷，您在深圳市福田区人民法院的（2026）粤0307民初2394号知识产权纠纷案件，已依法向您预留的邮箱982145926@gmail.com送达相关法律文书。您的身份证号后四位是1301。法院位置是朝南出发，经过银行后步行100米。价格是1988元。您看还有什么问题？欢迎和我沟通，我随时为您服务，再见。"
texts = [i["text"] for i in json.loads(frd.do_voicegen_frd(text))["sentences"]]
text = ''.join(texts)
print(text)
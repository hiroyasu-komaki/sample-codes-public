from transformers import pipeline

# ローカルに保存したモデルのパスを指定
model_path = "./fugumt-ja-en-local"

# ローカルパスからモデルを読み込み
fugu_translator = pipeline('translation', model=model_path)

# 翻訳を実行
result = fugu_translator('猫はかわいいです。')
print(result)
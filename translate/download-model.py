from transformers import pipeline

# モデルを指定したディレクトリにダウンロード
model_path = "./fugumt-ja-en-local"

print(f"Downloading model to {model_path}...")
fugu_translator = pipeline('translation', model='staka/fugumt-ja-en')

# ローカルに保存
fugu_translator.save_pretrained(model_path)
print(f"Model saved to {model_path}")
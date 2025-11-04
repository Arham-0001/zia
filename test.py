from openai import OpenAI

# ✅ Put your API key here
client = OpenAI(api_key="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"
)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you hear me?"}
        ]
    )

    print("\n✅ API Working Successfully!")
    print("Bot Reply:", response.choices[0].message.content)

except Exception as e:
    print("\n❌ API Error:")
    print(e)

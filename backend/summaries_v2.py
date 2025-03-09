import os
from openai import OpenAI

client = OpenAI(api_key='poliscope-key')


# Ensure output directory exists
summary_folder = "summaries"
bullet_folder = "bullet_points"
os.makedirs(bullet_folder, exist_ok=True)

# Process each summary file
for filename in os.listdir(summary_folder):
    if filename.endswith(".txt"):
        summary_path = os.path.join(summary_folder, filename)

        # Read summary text
        with open(summary_path, "r", encoding="utf-8") as file:
            summary_text = file.read()

        # Generate bullet points using OpenAI
        try:
            response = client.chat.completions.create(model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You extract key points from summaries in clear, concise bullet points."},
                {"role": "user", "content": f"Convert this summary into concise bullet points:\n\n{summary_text}"}
            ])

            bullet_points = response.choices[0].message.content

            # Save bullet points to file
            bullet_path = os.path.join(bullet_folder, f"bullet_{filename}")
            with open(bullet_path, "w", encoding="utf-8") as file:
                file.write(bullet_points)

            print(f"Saved bullet points: {bullet_path}")

        except Exception as e:  # Catch general exceptions (including OpenAI API errors)
            print(f"Error processing {filename}: {e}")

print("All summaries converted to bullet points in 'bullet_points' folder.")
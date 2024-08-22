import base64
import mimetypes
from pathlib import Path
import anthropic


def main():
    model = "claude-3-5-sonnet-20240620"
    client = client = anthropic.Anthropic()

    prompt = """This image is a 3x4 sprite grid of a pixelated thing (a character, object, plant, animal, etc.).

What is that thing?

Respond with, for example,
<caption>a white woman with blonde hair wearing a blue hat and a blue gown</caption>
<caption>a yellow lion with a large brown mane</caption>
    """

    for path in Path("input-sprites").glob("*.png"):
        output_path = path.parent / (path.stem + ".txt")
        if output_path.exists():
            continue

        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        with path.open("rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": encoded_string,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        response = client.messages.create(
            model=model,
            messages=messages,
            system="""You are an expert image captioner.

Begin each caption with <caption> and end it with </caption>. Only output the caption, nothing else, since your outputs will be used programmatically.

I already know that the input is a pixelated sprite map and it's subject is in various poses and directions, so you must not mention that (various poses, various directions, pixelated) in the caption.
""",
            max_tokens=512,
            stream=False,
            temperature=0.9,
        )
        output = response.content[0].text.strip()
        assert output.startswith("<caption>")
        assert output.endswith("</caption>")
        output = output[len("<caption>"):-len("</caption>")]

        print(f"{path}: {output}")

        output = "A pixelated 3x4 sprite map in the style of SPRT depicting " + output.lower()

        output_path = path.parent / (path.stem + ".txt")
        with output_path.open("w") as f:
            f.write(output)



if __name__ == "__main__":
    main()

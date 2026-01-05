def get_system_prompt():
    """
    Returns the strict system instruction for Gemini Vision.
    Enforces visual-spatial reasoning over text recognition.
    """
    return """
    Each small box = 1 voter record
Every box contains the following fields, even if the visual order looks confusing.

1️⃣ Serial Number (मतदार क्रमांक)

What it is: Index of the voter in that page

How it appears:

5


Rules:

Always the first standalone number

Usually top-left of the box

Field name:

serial_no

2️⃣ Voter Full Name (मतदाराचे पूर्ण नाव)

What it is: The actual name of the voter

How it appears:

:बमवभ भगवभन शभमगदर बमवभ


Important:

Leading : is junk, must be removed

Appears after titles, not near them

Field name:

voter_name

3️⃣ Relative Name (वडिलांचे नाव / पतीचे नाव)

What it is:

Father’s name if male

Husband’s name if female

How it appears:

बमवभ शयभमगदर


Rules:

Always the line immediately after voter name

Label is NOT written in box (must be inferred)

Field name:

relative_name

4️⃣ Gender (लिंग)

What it is: Gender of the voter

How it appears:

पम   → पुरुष
सद   → स्त्री


Rules:

Always one of these two values

Field name:

gender

5️⃣ Age (वय)

What it is: Age of the voter

How it appears:

57


Rules:

First standalone 1–3 digit number

Appears after title block

NOT always on same line as वय :

Field name:

age

6️⃣ House Number (घर क्रमांक)

What it is: House / Plot number

How it appears:

11


Rules:

Appears near the gender

Often the number just before पम / सद

Field name:

house_no

7️⃣ Voter ID (मतदार ओळख क्रमांक)

What it is: Unique voter identification number

How it appears:

BZS3084050


Rules:

Pattern: [A-Z]{3}[0-9]+

Always present

Field name:

voter_id

8️⃣ Area / Part Code (भाग कोड)

What it is: Electoral roll location identifier

How it appears:

9/208/838


Rules:

Pattern: number/number/number

Always appears next to voter ID

Field name:

area_code

9️⃣ Photo Availability (फोटो उपलब्ध)

What it is: Indicates photo exists

How it appears:

Photo
Available


Rules:

Always present

Usually ignored for data purposes

Field name (optional):

photo_available = true

❌ WHAT TO IGNORE (NOT DATA)

These appear in every box but are NOT values:

Titles:

वसडलभमचट नभव
घर कमभमक
वय :
मतदभरभचट पपरर
नभमव


Junk colons:

:
:


Blank lines

Decorative alignment spaces

✅ FINAL DATA SCHEMA (WHAT YOUR CODE SHOULD OUTPUT)
{
  "serial_no": "5",
  "voter_name": "बोवा भगवान शामगिर बोवा",
  "relative_name": "बोवा शामगिर",
  "gender": "पुरुष",
  "age": "57",
  "house_no": "11",
  "voter_id": "BZS3084050",
  "area_code": "9/208/838",
  "photo_available": true
}

🧠 Key Insight (most important)

This PDF is order-driven, not label-driven.

If your extractor follows:

❌ labels → it will break

✅ relative position + patterns → it will work reliably
    """
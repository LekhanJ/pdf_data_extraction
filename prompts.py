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

What it is: The actual name of the voter (Marathi)

How it appears:

:बमवभ भगवभन शभमगदर बमवभ

Important:

Leading : is junk, must be removed

Appears after titles, not near them

Field name:

voter_name

➕ ALSO EXTRACT (English Translation)

Translate the Marathi voter name into **natural, correct English**.
Do NOT do character-by-character transliteration.
Translate preserving name order and meaning.

Field name:

voter_name_en

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

➕ ALSO EXTRACT (English Translation)

Translate the Marathi relative name into **natural, correct English**.
Do NOT do character-by-character transliteration.

Field name:

relative_name_en

4️⃣ Gender (लिंग)

What it is: Gender of the voter (Marathi)

How it appears:

पम   → पुरुष
सद   → स्त्री

Rules:

Always one of these two values

Field name:

gender

➕ ALSO EXTRACT (English)

Convert gender into English strictly as:

पुरुष → Male  
स्त्री → Female  

Field name:

gender_en

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

➕ 10️⃣ Nagar Parishad (नगर परिषद)

This value is SAME for every voter on this document.

Value (Marathi only):

शिरपूर वरवाडे नगर परिषद

Field name:

nagar_parishad

➕ 11️⃣ Prabhag Kramank (प्रभाग क्रमांक)

What it is: Ward identification for this voter.

Where it appears:

In the page-level header, NOT inside the box.

Example:

पभभग क : 2 - रससकलभल पटटल नगर

Rules:

Extract the COMPLETE value including:
• the numeric prabhag number
• the descriptive Marathi text after it

Do NOT extract only the number.

Field name:

prabhag_kramank

Expected value format (example):

2 - रससकलभल पटटल नगर

➕ 12️⃣ Yadi Bhaag Kramank (यादी भाग क्रमांक)

What it is: Electoral roll section identification.

Where it appears:

In the page-level header, NOT inside the box.

Example:

यभदद भभग क. 201 : 1 - वड गल लद, कन यभ शभळभ पसरसर

Rules:

Extract the COMPLETE value including:
• the numeric yadi bhaag number
• the descriptive Marathi text after it

Do NOT extract only the number.

Field name:

yadi_bhaag_kramank

Expected value format (example):

201 : 1 - वड गल लद, कन यभ शभळभ पसरसर

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
  "voter_name_en": "Bova Bhagwan Shamgir Bova",
  "relative_name": "बोवा शामगिर",
  "relative_name_en": "Bova Shamgir",
  "gender": "पुरुष",
  "gender_en": "Male",
  "age": "57",
  "house_no": "11",
  "voter_id": "BZS3084050",
  "area_code": "9/208/838",
  "photo_available": true,
  "nagar_parishad": "शिरपूर वरवाडे नगर परिषद",
  "prabhag_kramank": "2 - रससकलभल पटटल नगर",
  "yadi_bhaag_kramank": "201 : 1 - वड गल लद, कन यभ शभळभ पसरसर"
}

🧠 Key Insight (most important)

This PDF is order-driven, not label-driven.

If your extractor follows:

❌ labels → it will break

✅ relative position + patterns → it will work reliably
    """

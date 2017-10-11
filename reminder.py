
import smtplib
import sys
import os
import csv

email_template = """\
From: %s
To: %s
Subject: %s
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Disposition: inline
Content-Transfer-Encoding: 8bit

%s
"""

def send_email(gmail_user, gmail_password, sender, to_email, subject, body):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        sent_from = gmail_user
        to = [to_email]
        receivers = []
        receivers.extend(to)
        receivers.append(gmail_user)
        email_text = email_template % (sender, ", ".join(receivers), subject, body)
        server.sendmail(sent_from, [to], email_text.encode('utf8'))
        server.close()
        print('Email sent!')
    except Exception as e:
        print('Something went wrong... ' + str(e))

PARTS = [
    ('kursens syfte och lärandemål' ,'purpose'),
    ('examinator, föreläsare, övnings-/laborationshandledare, administrativ personal samt deras kontaktuppgifter', 'examiner'),
    ('kurslitteratur', 'litterature'),
    ('plan för föreläsningar, övningar och laborationer', 'plan'),
    ('en sammanfattning av gjorda förändringar sedan förra tillfälle', 'changes'),
    ('form för examinationen', 'examination_form'),
    ('betygsgränser och eventuella övriga krav för att bli godkänd på kursen (obligatoriska moment)', 'grading_scale'),
    ('hur obligatoriska moment bidrar till slutbetyget', 'mandatory_parts'),
    ('hur frivilliga moment bidrar till bedömningen av de studerandes kunskaper och färdigheter såsom resultat på duggor', 'volentary_parts'),
    ('tillåtna hjälpmedel vid examination, samt om markeringar, indexeringar samt anteckningar i hjälpmedel är tillåtna', 'exam_aids'),
    ('tid och plats för examination (ordinarie tentamenstillfälle) (Pratat med Tandlös, vi tror att det räcker med datum)', 'exam_time'),
]

SUBJECT_SV = "Påminnelse om kurs-PM"
SUBJECT_EN = "Reminder of course PM"

INTRO_SV = """Hej {},

Vi hoppas att allting är bra och att du ser fram emot din kurs kommande läsperiod.

Vi skriver för det snart är kursstart i kursen {}, och för att det enligt Chalmers föreskrifter för examination skall finnas ett komplett kurs-pm tillgängligt på kurshemsidan två veckor innan kursstart. Du kan läsa föreskrifterna här: {} \n

Vi kan se att det saknas information om en del saker listat nedan:
"""

INTRO_EN = """Hello {},

We hope that everything is well with you.

We are writing to remind you that today there are two weeks until course start for the course {}, and according to Chalmers rules for examination there should be a complete course PM available at the course home page. You can read about them here: {} \n

We can see that some information is missing regarding:
"""

TENTA_LINK_SV = 'https://student.portal.chalmers.se/sv/chalmersstudier/regelsamling/Sidor/F%C3%B6reskrifter-examination.aspx'
TENTA_LINK_EN = 'https://student.portal.chalmers.se/en/chalmersstudies/joint-rules-and-directives/Pages/Rules-for-examinations.aspx'

PARTS_SV = {
	"purpose": "kursens syfte och lärandemål",
	"examiner": "examinator, föreläsare, övnings-/laborationshandledare, administrativ personal samt deras kontaktuppgifter",
	"litterature": "kurslitteratur",
	"plan": "plan för föreläsningar, övningar och laborationer",
	"changes": "en sammanfattning av gjorda förändringar sedan förra tillfället",
	"examination_form": "form för examinationen",
	"grading_scale": "betygsgränser och eventuella övriga krav för att bli godkänd på kursen (obligatoriska moment)",
	"mandatory_parts": "hur obligatoriska moment bidrar till slutbetyget",
	"volentary_parts": "hur frivilliga moment bidrar till bedömningen av de studerandes kunskaper och färdigheter såsom resultat på duggor",
	"exam_aids": "tillåtna hjälpmedel vid examination, samt om markeringar, indexeringar samt anteckningar i hjälpmedel är tillåtna,",
	"exam_time": "tid och plats för examination (ordinarie tentamenstillfälle)",
	"course_page": "Kurshemsida som kan nås från studentportalen"
}

PARTS_EN = {
    "purpose": "purpose and intended learning outcomes of the course",
    "examiner": "examiner, lecturers, exercise and laboratory advisers, administrative personnel and their contact details",
    "litterature": "reading list",
    "plan": "plan for lectures, exercises and laboratory sessions",
    "changes": "summary of changes since the course was given last",
    "examination_form": "examination format",
    "grading_scale": "grade limits and any other requirements for passing the course (required activities)",
    "mandatory_parts": "how required activities contribute to the final grade",
    "volentary_parts": "how optional activities, such as test results, contribute to assessment of the student’s knowledge and skills",
    "exam_aids": "authorised aids at examinations, and whether markings, indexing and notes are permitted on the aids",
    "exam_time": "time and place of examinations (ordinary examination schedule)",
}

OUTRO_SV = """Vi ser fram emot en intressant läsperiod, och vi kommer att göra vårt bästa för att hjälpa till så att kursen blir så bra som möjligt.\n

Ha en fortsatt trevlig dag

Med vänliga hälsningar
snIT - studienämnden på IT"""

OUTRO_EN = """We look forward to an interesting study period, and we will do our best to ensure that the course is as good as possible.

Have a good day!
snIT - Student Educational Committee IT
"""

def get_subject(lang):
    if lang == "sv":
        return SUBJECT_SV
    elif lang == "en":
        return SUBJECT_EN

def get_intro(examiner_first_name, course_code, lang):
    intro = ""
    if lang == "sv":
        intro = INTRO_SV
    elif lang == "en":
        intro = INTRO_EN

    return intro.format(examiner_first_name, course_code, TENTA_LINK_SV)

def get_parts(missing, lang):
    output = ""
    prefix = "   • "
    parts = dict()

    if lang == "sv":
        parts = PARTS_SV
    elif lang == "en":
        parts = PARTS_EN

    for p in missing:
        output = output + prefix + parts.get(p) + "\n"
    output = output + "\n"
    return output

def get_missing_parts(row):
    missing = []
    for part, key in PARTS:
        if not row.get(part):
            missing.append(key)

    return missing

def get_outro(lang):
    if lang == 'sv':
        return OUTRO_SV
    elif lang == "en":
        return OUTRO_EN


def email_responsible(row, missing):
    s = "{} {}".format(row.get('Kurs'), missing)
    print(s)
    examiner_first_name = row.get('Kursansvarig').strip()
    examiner_email = row.get('email (examinator)').strip()
    course_code = row.get('Kurs').strip()
    lang = 'sv'
    language_supplied = row.get('Språk', '').strip()
    if language_supplied == 'en':
        lang = 'en'

    intro = get_intro(examiner_first_name, course_code, lang)
    parts = get_parts(missing, lang)
    outro = get_outro(lang)

    gmail_user = # TODO gmail account email here, perhaps new one for snIT?
    gmail_password = # TODO PASSWORD HER

    sender = 'snit@chalmers.it'
    to = '' #TODO Add examiner email from row here

    subject = get_subject(lang)
    body = intro + parts + outro

    send_email(gmail_user, gmail_password, sender, to, subject, body)
    return lang



def process(input_file):
    sv = 0
    en = 0
    reader = csv.DictReader(open(input_file, newline=''))
    for row in reader:
        if not row.get('Kurs'):
            continue

        lang = 'sv'
        language_supplied = row.get('Språk', '').strip()
        if language_supplied == 'en':
            lang = 'en'

        if lang == 'sv' and sv > 0:
            continue

        if lang == 'en' and en > 0:
            continue

        missing = get_missing_parts(row)
        if missing:
            l = email_responsible(row, missing)
            if l == sv:
                sv = sv + 1
            elif l == en:
                en = en + 1


if __name__ == '__main__':
    input_file = sys.argv[1]
    process(input_file)

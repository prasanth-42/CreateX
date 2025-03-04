from flask import Flask, render_template, request, jsonify
import language_tool_python

app = Flask(__name__)

# Initialize LanguageTool
tool = language_tool_python.LanguageTool('en-US')

# Offensive words list
offensive_words = [
    "ass", "asshole", "bastard", "bitch", "blowjob", "bollocks", "boner", "boob", "bullshit", "butt",
    "cameltoe", "carpetmuncher", "clit", "cock", "coon", "crap", "cum", "cunt", "damn", "dick",
    "dickhead", "dildo", "dyke", "fag", "faggot", "fellatio", "fuck", "fucker", "fucking", "gangbang",
    "gay", "goddamn", "gook", "hell", "homo", "hump", "jackass", "jerk", "jerkoff", "jizz",
    "knob", "kraut", "kunt", "lesbian", "lezzie", "lube", "muff", "nazi", "nigger", "nigga",
    "nut", "nutsack", "orgasm", "paki", "penis", "piss", "pissed", "pisser", "pissflaps", "poop",
    "poon", "porn", "pube", "pussy", "queef", "queer", "rectum", "rimjob", "schlong", "scrotum",
    "semen", "sex", "shag", "shit", "shithead", "shithole", "shitter", "skank", "slag", "slut",
    "smegma", "snatch", "spastic", "spunk", "tit", "tits", "tosser", "turd", "twat", "twink",
    "twinkie", "vag", "vagina", "wank", "wanker", "whore", "wop", "yid", "arse", "arsehole",
    "balls", "beaver", "bellend", "bloody", "bugger", "bum", "choad", "clunge", "cockup", "coon",
    "crack", "crotch", "cucumber", "cumshot", "cunnilingus", "dickwad", "dike", "dilldo", "dong",
    "douche", "ejaculate", "fart", "feck", "felch", "flange", "fudgepacker", "gash", "gobshite",
    "gooch", "gypo", "handjob", "heeb", "hobo", "honkey", "hump", "jizzum", "junk", "kike",
    "knobend", "labia", "mcfly", "minge", "molester", "muffdiver", "mung", "nads", "nig", "nipple",
    "nonce", "nutjob", "nuts", "pecker", "peckerwood", "pedo", "phallus", "pillock", "plonker",
    "poonani", "prick", "queer", "rape", "rim", "rimming", "rump", "rusty", "sack", "scrote",
    "scum", "shag", "shart", "shite", "skank", "slapper", "smeg", "spastic", "spunk", "tinkle",
    "todger", "toss", "turd", "wad", "wang", "wank", "wanker", "weiner", "whacker", "willie",
    "willy", "yank", "yankoff", "yellow", "yid","anal", "arse", "arsehole", "ass", "asshat", "asshole", "bampot", "bastard", "beaner", "bellend",
    "bint", "bitch", "bollocks", "bollox", "boner", "boob", "booby", "bullshit", "bullshite", "bum",
    "bumblefuck", "butt", "butthole", "carpetmuncher", "chav", "choad", "clit", "clunge", "cock", "cockhead",
    "cockup", "coon", "cooter", "cracker", "crap", "cum", "cunt", "damn", "dick", "dickhead", "dildo",
    "dipshit", "douche", "douchebag", "dyke", "fag", "faggot", "feck", "felch", "fellatio", "fuck",
    "fucker", "fuckface", "fuckhead", "fucking", "fudgepacker", "gaylord", "gimp", "gobshite", "goddamn",
    "gooch", "gook", "gypo", "heeb", "hell", "hobo", "homo", "honkey", "hump", "jackass", "jerk",
    "jerkoff", "jizz", "jizzum", "jock", "kike", "knob", "knobend", "kraut", "kunt", "labia", "lesbo",
    "lezzie", "lube", "mcfly", "minge", "molester", "motherfucker", "muff", "muffdiver", "mung", "nads",
    "nazi", "nigger", "nigga", "nonce", "nut", "nuts", "nutsack", "paki", "penis", "piss", "pissed",
    "pisser", "pissflaps", "poop", "poon", "poonani", "porn", "prick", "pube", "pussy", "queef", "queer",
    "rape", "rectum", "rim", "rimjob", "rump", "rusty", "sack", "schlong", "scrote", "scrotum", "semen",
    "sex", "shag", "shart", "shit", "shithead", "shithole", "shitter", "skank", "slag", "slapper",
    "slut", "smeg", "smegma", "snatch", "spastic", "spunk", "tart", "tit", "tits", "todger", "tosser",
    "turd", "twat", "twink", "twinkie", "vag", "vagina", "wad", "wang", "wank", "wanker", "weiner",
    "whacker", "whore", "willie", "willy", "wop", "yank", "yankoff", "yid", "zipperhead"


]


def validate_script(script):
    issues = []

    # 1. Grammar & Spelling Check
    matches = tool.check(script)
    grammar_errors = len(matches)

    if grammar_errors > 0:
        grammar_feedback = [{"type": match.ruleIssueType, "message": match.message}
                            for match in matches[:5]]  # Show first 5 issues
        issues.append({
            "category": "Grammar & Spelling",
            "count": grammar_errors,
            "details": grammar_feedback
        })

    # 2. Word & Sentence Limits
    words = script.split()
    word_count = len(words)
    sentence_count = script.count('.') + script.count('?') + script.count('!')

    structure_issues = []
    if word_count < 50:
        structure_issues.append("The script should have at least 50 words")
    if word_count > 1000:
        structure_issues.append("The script exceeds 1000 words")
    if sentence_count < 5:
        structure_issues.append("The script should have at least 5 sentences")

    if structure_issues:
        issues.append({
            "category": "Structure",
            "details": structure_issues
        })

    # 3. Offensive Language Detection
    found_offensive = [word for word in offensive_words if word in script.lower()]
    if found_offensive:
        issues.append({
            "category": "Inappropriate Content",
            "details": [f"Found inappropriate words: {', '.join(found_offensive)}"]
        })

    return issues


@app.route('/')
def home():
    return render_template('script_validation.html')


@app.route('/validate', methods=['POST'])
def validate():
    script = request.json.get('script', '')

    if not script.strip():
        return jsonify({'error': 'Please enter a script'}), 400

    try:
        validation_results = validate_script(script)
        return jsonify({
            'issues': validation_results,
            'hasIssues': len(validation_results) > 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
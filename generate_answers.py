#!/usr/bin/env python3
"""
Generate merge_answers.md from merge.md.
Shows only the question text and correct answer for each matched DE/EN pair.
"""
import re

SKIP_QUESTIONS = {64, 72, 73, 194, 213, 222, 224, 238, 239, 252, 268, 281, 282, 298}

# Translation mappings: English key phrase -> German key phrase
# Used to help match English [x] answer to corresponding German option
TRANSLATION_HINTS = {
    # Common terms
    "basic law": "grundgesetz",
    "freedom of opinion": "meinungsfreiheit",
    "freedom of religion": "religionsfreiheit",
    "freedom of faith": "glaubens",
    "human dignity": "menschenwürde",
    "freedom of assembly": "versammlungsfreiheit",
    "press freedom": "pressefreiheit",
    "press censorship": "pressezensur",
    "freedom of movement": "freizügigkeit",
    "unconstitutional": "verfassungswidrig",
    "constitutional": "rechtsstaatl",
    "republic": "republik",
    "federal state": "bundesstaat",
    "federal chancellor": "bundeskanzler",
    "federal president": "bundespräsident",
    "bundesrat": "bundesrat",
    "bundestag": "bundestag",
    "eagle": "adler",
    "coalition": "koalition",
    "democracy": "demokrat",
    "dictatorship": "diktatur",
    "monarchy": "monarch",
    "legislature": "legislativ",
    "executive": "exekutiv",
    "judiciary": "judikat",
    "judicial power": "rechtsprechend",
    "legislative power": "gesetzgeb",
    "executive power": "vollzieh",
    "social insurance": "sozialversicherung",
    "health insurance": "krankenversicherung",
    "unemployment insurance": "arbeitslosenversicherung",
    "pension": "renten",
    "long-term care": "pflege",
    "life insurance": "lebensversicherung",
    "trade union": "gewerkschaft",
    "employees": "arbeitnehmer",
    "employers": "arbeitgeber",
    "labor court": "arbeitsgericht",
    "federal constitutional court": "bundesverfassungsgericht",
    "minister-president": "ministerpräsident",
    "christian democratic union": "christlich demokratische union",
    "christian social union": "christlich soziale union",
    "social democratic": "sozialdemokr",
    "free democratic": "freie demokratische",
    "traffic light": "ampel",
    "opposition": "opposition",
    "parliamentary group": "fraktion",
    "constitution": "verfassung",
    "social market economy": "soziale marktwirtschaft",
    "planned economy": "planwirtschaft",
    "market economy": "marktwirtschaft",
    "popular sovereignty": "volkssouverän",
    "state power": "staatsgewalt",
    "separation": "getrennt",
    "inviolable": "unantastbar",
    "asylum": "asyl",
    "monetary fines": "geldstrafe",
    "forced labor": "zwangsarbeit",
    "berlin": "berlin",
    "munich": "münchen",
    "north rhine": "nordrhein",
    "mecklenburg": "mecklenburg",
    "saxony-anhalt": "sachsen-anhalt",
    "saxony": "sachsen",
    "thuringia": "thüringen",
    "brandenburg": "brandenburg",
    "warsaw pact": "warschauer pakt",
    "nato": "nato",
    "european union": "europäischen union",
    "gdr": "ddr",
    "stasi": "stasi",
    "holocaust": "holocaust",
    "synagogue": "synagoge",
    "church": "kirche",
    "mosque": "moschee",
    "advent": "advent",
    "christmas": "weihnacht",
    "easter": "ostern",
    "pentecost": "pfingst",
    "rose monday": "rosenmontag",
    "turkey": "türkei",
    "italy": "italien",
    "poland": "polen",
    "denmark": "dänemark",
    "luxembourg": "luxemburg",
    "czech": "tschech",
    "netherlands": "niederländ",
    "switzerland": "schweiz",
    "france": "frankreich",
    "soviet union": "sowjetunion",
    "great britain": "großbritannien",
    "usa": "usa",
    "strasbourg": "straßburg",
    "mayor": "bürgermeister",
    "municipality": "gemeinde",
    "youth welfare": "jugendamt",
    "registry office": "standesamt",
    "works council": "betriebsrat",
    "notice period": "kündigungsfrist",
    "value-added tax": "umsatzsteuer",
    "church tax": "kirchensteuer",
    "guest worker": "gastarbeiter",
    "stumbling stone": "stolperstein",
    # Q5 and similar: political/voting vocab
    "voter": "wähler",
    "influenced": "beeinflusst",
    "forced": "gezwungen",
    "disadvantages": "nachteile",
    "accept money": "geld annehmen",
    "prison": "gefängnis",
    "eligible voters must vote": "wahlberechtigten",
    "governing party": "regierungspartei",
    "governing parties": "regierenden parteien",
    "all members of parliament who do not belong": "alle abgeordneten",
    "parliamentary group": "fraktion",
    "5% threshold": "5%-hürde",
    "reached the 5%": "5%-hürde erreichen",
    "all parties": "alle parteien",
    # Social/family vocab
    "parents": "eltern",
    "children": "kinder",
    "family": "famili",
    "marriage": "ehe",
    "divorced": "geschieden",
    "pregnant": "schwanger",
    "child benefit": "kindergeld",
    # Legal vocab
    "punished": "bestraft",
    "arrested": "verhaftet",
    "criminal": "straftat",
    "court": "gericht",
    "penalty": "strafe",
    "fine": "geldstrafe",
    "imprisonment": "freiheitsstrafe",
    "innocent": "unschuldig",
    "convicted": "verurteilt",
    # Work/employment vocab
    "dismissed": "entlassen",
    "fired": "entlassen",
    "employed": "angestellt",
    "employee": "arbeitnehmer",
    "employer": "arbeitgeber",
    "salary": "gehalt",
    "wage": "lohn",
    "income tax": "lohnsteuer",
    "self-employed": "selbstständig",
    "apprenticeship": "lehrstelle",
    "training": "ausbildung",
    "lifelong learning": "weiter lernen",
    # Administrative vocab
    "registration": "anmeldung",
    "residents registration": "einwohnermeldeamt",
    "tax return": "steuererklärung",
    "objection": "widerspruch",
    "authority": "behörde",
    "complaint": "beschwerde",
    # Education
    "school diploma": "schulabschluss",
    "compulsory attendance": "anwesenheitspflicht",
    "private school": "privatschule",
    # Health/social
    "accident insurance": "unfallversicherung",
    "disability": "behinderung",
    "wheelchair": "rollstuhl",
    "discrimination": "diskriminierung",
    "equal treatment": "gleichbehandlung",
    # Elections
    "candidate": "kandidat",
    "election notification": "wahlbenachrichtigung",
    "polling station": "wahllokal",
    "mail vote": "briefwahl",
    "ballot": "stimmzettel",
    "second vote": "zweitstimme",
    "first vote": "erststimme",
    "representatives": "abgeordnete",
    # History
    "berlin wall": "berliner mauer",
    "occupation zone": "besatzungszone",
    "allied": "alliierten",
    "air lift": "luftbrücke",
    "reunification": "wiedervereinigung",
    "cold war": "kalten krieg",
    "uprising": "aufstand",
    "crimes against jews": "verbrechen gegen juden",
    "economic miracle": "wirtschaftswunder",
    # German states
    "hesse": "hessen",
    "bavaria": "bayern",
    "lower saxony": "niedersachsen",
    "north rhine-westphalia": "nordrhein-westfalen",
    "rhineland-palatinate": "rheinland-pfalz",
    "saxony-anhalt": "sachsen-anhalt",
    "schleswig-holstein": "schleswig-holstein",
    "saarland": "saarland",
    "berlin": "berlin",
    "hamburg": "hamburg",
    "bremen": "bremen",
    "mecklenburg-western pomerania": "mecklenburg-vorpommern",
    # EU/international
    "european parliament": "europäischen parlaments",
    "european commission": "europäische kommission",
    "european economic community": "europäische wirtschaftsgemeinschaft",
    "schengen": "schengen",
    "passport control": "passkontrolle",
    "member states": "mitgliedstaaten",
    "roman treaties": "römischen verträge",
    "founding member": "gründungsmitglied",
    # Misc
    "night rest": "nachtruhe",
    "house rules": "hausordnung",
    "recipe": "rezept",
    "restaurant license": "gaststättenerlaubnis",
    "television": "fernseher",
    "bus line": "buslinie",
    "swimming pool": "schwimmbad",
    "club": "verein",
    "honorary": "ehrenamtl",
    "petition": "petition",
    "citizens initiative": "bürgerinitiative",
    "mosque": "moschee",
    "faith": "glauben",
    "believe": "glauben",
    "christian": "christl",
    "christmas tree": "tannenbaum",
    "painting eggs": "eier bemalen",
    "pumpkins": "kürbisse",
    "costumes": "kostüme",
    "rose monday": "rosenmontag",
    "advent season": "adventszeit",
    "advent": "advent",
    "turkey": "türkei",
    "italy": "italien",
    "migrants": "migrant",
    "iron curtain": "eisernen vorhang",
    "airlift": "luftbrücke",
    "order of merit": "bundesverdienstkreuz",
    "lay judge": "schöff",
    "prosecutor": "staatsanwalt",
    "judge": "richter",
    "lawyer": "rechtsanwalt",
    "trial": "prozess",
    "municipalities": "gemeinden",
    "active suffrage": "aktives wahlrecht",
    "5% threshold": "5%-hürde",
    "ballot": "stimmzettel",
    "mail": "briefwahl",
    "compulsory schooling": "schulpflicht",
    "parental allowance": "elterngeld",
    "maternity protection": "mutterschutz",
    "parental leave": "elternzeit",
    "abitur": "abitur",
    "evening gymnasium": "abendgymnasium",
    "kindergarten": "kindergartenplatz",
    "continuing education": "weiterbildung",
    "secrecy of correspondence": "briefgeheimnis",
    "painting eggs": "eier bemalen",
    "christmas tree": "tannenbaum",
    "willy brandt": "willy brandt",
    "konrad adenauer": "konrad adenauer",
    "helmut kohl": "helmut kohl",
    "helmut schmidt": "helmut schmidt",
    "frank-walter steinmeier": "steinmeier",
    "olaf scholz": "olaf scholz",
    "1933": "1933",
    "1945": "1945",
    "1949": "1949",
    "1961": "1961",
    "1989": "1989",
    "1990": "1990",
    "1938": "1938",
    "1953": "1953",
    "1700 years": "1700",
    "1150 years": "1150",
    "700 years": "700",
    "300 years": "300",
    "16": "16",
    "14": "14",
    "18": "18",
    "5%": "5%",
    "4 years": "4 jahre",
    "2 years": "2 jahre",
    "3 years": "3 jahre",
    "5 years": "5 jahre",
    "27": "27",
    "83 million": "84 million",  # skip via SKIP_QUESTIONS
    "national socialist": "nationalsozialist",
    "third reich": "dritten reich",
    "world war ii": "zweiten weltkrieg",
    "world war i": "ersten weltkrieg",
    "july 20": "20. juli",
    "november 9": "9. november",
    "june 17": "17. juni",
    "may 8": "8. mai",
    "may day": "maifeiertag",
    "right to vote": "wahlrecht",
    "all residents": "alle einwohner",
    "gun ownership": "waffenbesitz",
    "everyone is equal": "alle sind vor dem gesetz gleich",
    "everyone should have the same amount of money": "alle sollen gleich viel geld haben",
    "social balance": "sozialen ausgleich",
    "supply and demand": "angebot und nachfrage",
    "eu": "eu",
    "1 = great britain": "1=großbritannien",
    "soviet occupation zone": "sowjetischen besatzungszone",
    "american occupation zone": "amerikanischen besatzungszone",
    "japan": "japan",
    "alsace-lorraine": "elsass-lothringen",
    "unified germany": "einheit",
    "objection": "widerspruch",
    "willingness for lifelong learning": "weiter lernen",
    "national socialist crimes against jews": "nationalsozialistischen verbrechen gegen juden",
    "christianity": "christentum",
    "protest":  "protest",
}


def parse_questions(content):
    """Parse merge.md into a list of question blocks."""
    # Split on question headers
    blocks = re.split(r'(?=### \d+\.)', content)
    questions = {}

    for block in blocks:
        if not block.strip():
            continue
        # Parse question number
        m = re.match(r'### (\d+)\.(.+?)(?:\n)((?:.*\n)*)', block, re.DOTALL)
        if not m:
            continue
        num = int(m.group(1))
        q_text = m.group(2).strip()
        options_text = m.group(3)

        # Parse options (handles both "- [ ] text" and "- [ ]text" formats)
        options = re.findall(r'- \[([ x])\] ?(.+)', options_text)

        # Determine if German (no [x]) or English (has [x])
        has_answer = any(o[0] == 'x' for o in options)
        correct_answer = None
        if has_answer:
            for o in options:
                if o[0] == 'x':
                    correct_answer = o[1].strip()
                    break

        entry = {
            'num': num,
            'question': q_text,
            'options': [o[1].strip() for o in options],
            'correct': correct_answer,
            'is_english': has_answer
        }

        if num not in questions:
            questions[num] = {}
        if has_answer:
            questions[num]['en'] = entry
        else:
            questions[num]['de'] = entry

    return questions


def option_similarity(en_opt, de_opt):
    """Compute cross-lingual similarity between English and German option strings."""
    en_lower = en_opt.lower()
    de_lower = de_opt.lower()
    score = 0

    # Check translation hints
    for en_key, de_key in TRANSLATION_HINTS.items():
        if en_key in en_lower and de_key.lower() in de_lower:
            score += len(en_key) * 2

    # Shared numbers/years/percentages
    en_numbers = re.findall(r'\b\d+\b', en_lower)
    de_numbers = re.findall(r'\b\d+\b', de_lower)
    for n in en_numbers:
        if n in de_numbers:
            score += 15

    # Shared proper nouns (capitalized words in English that appear in German)
    en_proper = set(re.findall(r'\b[A-Z][a-zA-Zäöüß]{2,}\b', en_opt))
    for word in en_proper:
        if word.lower() in de_lower:
            score += 8

    # Cognate detection: words that share a long common prefix (>=4 chars)
    en_words = re.findall(r'\b[a-zA-Z]{4,}\b', en_lower)
    de_words = re.findall(r'\b[a-zA-ZäöüßÄÖÜ]{4,}\b', de_lower)
    for ew in en_words:
        for dw in de_words:
            # Find longest common prefix
            min_len = min(len(ew), len(dw))
            common_prefix = 0
            for i in range(min_len):
                if ew[i] == dw[i]:
                    common_prefix += 1
                else:
                    break
            if common_prefix >= 4:
                score += common_prefix

    return score


def find_german_answer_bipartite(de_options, en_options, en_correct_idx):
    """
    Use bipartite matching to align all German and English options,
    then return the German option corresponding to the English correct answer.
    """
    n = len(de_options)
    m = len(en_options)
    if n == 0 or m == 0:
        return None

    # Build similarity matrix [n x m]
    sim_matrix = []
    for i, de_opt in enumerate(de_options):
        row = []
        for j, en_opt in enumerate(en_options):
            row.append(option_similarity(en_opt, de_opt))
        sim_matrix.append(row)

    # Greedy bipartite matching: repeatedly pick max similarity pair
    matched_de = {}  # de_idx -> en_idx
    used_en = set()
    used_de = set()

    # Find best matches greedily
    while len(used_de) < n and len(used_en) < m:
        best_score = -1
        best_i, best_j = -1, -1
        for i in range(n):
            if i in used_de:
                continue
            for j in range(m):
                if j in used_en:
                    continue
                if sim_matrix[i][j] > best_score:
                    best_score = sim_matrix[i][j]
                    best_i, best_j = i, j
        if best_score <= 0 or best_i == -1:
            break
        matched_de[best_j] = best_i  # en_idx -> de_idx
        used_en.add(best_j)
        used_de.add(best_i)

    # If we found a match for the correct English answer
    if en_correct_idx in matched_de:
        return de_options[matched_de[en_correct_idx]]

    # If no high-confidence match, use position
    if en_correct_idx < len(de_options):
        return de_options[en_correct_idx]

    return None


def find_german_answer(de_options, en_correct):
    """Find the German option that matches the English correct answer (single option version)."""
    en_lower = en_correct.lower()

    scores = []
    for de_opt in de_options:
        scores.append(option_similarity(en_correct, de_opt))

    if not scores:
        return None

    max_score = max(scores)
    if max_score > 0:
        return de_options[scores.index(max_score)]

    return None


def main():
    with open('merge.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix Q263: continuation line "### 14. Jahre..." is part of Q263 question text, not Q14
    content = content.replace(
        'Das bedeutet: Jugendliche, die\n### 14. Jahre und älter sind',
        'Das bedeutet: Jugendliche, die 14. Jahre und älter sind'
    )
    # Fix Q263 English equivalent if needed
    content = content.replace(
        'This means: Young people who are 14 years and older',
        'This means: Young people who are 14 years and older'
    )

    questions = parse_questions(content)

    output_lines = []
    output_lines.append('# Test "Leben in Deutschland" – Merged Answers (DE/EN)\n')
    output_lines.append('> German questions are shown first (with marked correct answer), followed by the English translation (with marked answer).\n\n')

    skipped = []
    processed = []
    no_match = []

    for num in sorted(questions.keys()):
        if num in SKIP_QUESTIONS:
            skipped.append(num)
            continue

        pair = questions[num]
        if 'de' not in pair or 'en' not in pair:
            no_match.append(num)
            continue

        de = pair['de']
        en = pair['en']

        en_correct = en['correct']

        # Find the index of the correct English answer
        en_correct_idx = None
        for i, opt in enumerate(en['options']):
            if opt == en_correct:
                en_correct_idx = i
                break

        if en_correct_idx is None:
            no_match.append(num)
            de_answer = de['options'][0] if de['options'] else None
        elif len(de['options']) == 0:
            no_match.append(num)
            de_answer = None
        else:
            # Try bipartite matching
            de_answer = find_german_answer_bipartite(
                de['options'], en['options'], en_correct_idx
            )
            if de_answer is None:
                no_match.append(num)
                de_answer = de['options'][en_correct_idx] if en_correct_idx < len(de['options']) else de['options'][0]

        # Format output
        output_lines.append(f"### {num}. {de['question']}\n")
        output_lines.append(f"- [x] {de_answer}\n\n")
        output_lines.append(f"### {num}. {en['question']}\n")
        output_lines.append(f"- [x] {en_correct}\n\n")
        processed.append(num)

    with open('merge_answers.md', 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f"Processed: {len(processed)} questions")
    print(f"Skipped (mismatched): {len(skipped)} - {skipped}")
    print(f"Issues (no match/fallback used): {len(no_match)} - {no_match}")


if __name__ == '__main__':
    main()

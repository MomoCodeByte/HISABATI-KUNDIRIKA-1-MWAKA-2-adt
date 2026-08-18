import asyncio
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = Path(__file__).resolve().parent / "vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))
VOICE = "sw-TZ-RehemaNeural"
RATE = "-10%"

CONFIG = {
    3: {"replace": {
        "pg003_n0005": "Namba nzima, ukurasa wa ADT 7.",
        "pg003_n0007": "Mpangilio wa namba nzima, ukurasa wa ADT 23.",
        "pg003_n0009": "Namba za Kirumi, ukurasa wa ADT 33.",
        "pg003_n0011": "Kujumlisha namba nzima, ukurasa wa ADT 42.",
        "pg003_n0013": "Kutoa namba nzima, ukurasa wa ADT 52.",
        "pg003_n0015": "Kuzidisha namba nzima, ukurasa wa ADT 62.",
        "pg003_n0017": "Kugawanya namba nzima, ukurasa wa ADT 77.",
        "pg003_n0019": "Sehemu, ukurasa wa ADT 91.",
    }},
    4: {"replace": {
        "pg004_n0002": "Wakati, ukurasa wa ADT 107.",
        "pg004_n0004": "Vipimo vya metriki, ukurasa wa ADT 129.",
        "pg004_n0006": "Fedha ya Tanzania, ukurasa wa ADT 145.",
        "pg004_n0008": "Maumbo, ukurasa wa ADT 159.",
        "pg004_n0010": "Takwimu, ukurasa wa ADT 179.",
    }},
    7: {
        "replace": {
            "pg007_n0010": "Zoezi la Kwanza. Marudio.",
            "pg007_n0012": "2. Soma namba zilizopo katika jedwali lifuatalo, kisha",
        },
        "after": {
            "pg007_n0011": ["Picha ina mistari mitatu ya mananasi. Mstari wa kwanza una mananasi kumi na sita. Mstari wa pili una mananasi kumi na sita. Mstari wa tatu una mananasi kumi na sita. Jumla kuna mananasi mangapi?"],
            "pg007_n0012": ["Ziandike kwa maneno. Namba ya kwanza imeandikwa kama mfano. Namba 86. Kwa maneno ni themanini na sita. Namba 39 itaandikwaje kwa maneno? Namba 475 itaandikwaje kwa maneno? Namba 884 itaandikwaje kwa maneno? Namba 706 itaandikwaje kwa maneno? Namba 912 itaandikwaje kwa maneno?"],
        },
    },
    8: {
        "replace": {
            "pg008_n0001": "Swali la 3. Andika namba zifuatazo kwa tarakimu. Mstari wa kwanza",
            "pg008_n0003": "Jedwali lina safu mbili: namba kwa maneno, na namba kwa tarakimu.",
            "pg008_n0004": "Mstari wa kwanza ni mfano. Namba kwa maneno ni hamsini na saba. Kwa tarakimu ni 57.",
            "pg008_n0005": "Mstari wa pili ni mfano. Namba kwa maneno ni mia sita kumi na mbili. Kwa tarakimu ni 612.",
            "pg008_n0006": "Mstari wa tatu. Ishirini na mbili itaandikwaje kwa tarakimu?",
            "pg008_n0007": "Mstari wa nne. Themanini na moja itaandikwaje kwa tarakimu?",
            "pg008_n0008": "Mstari wa tano. Mia tatu hamsini na tano itaandikwaje kwa tarakimu?",
            "pg008_n0009": "Mstari wa sita. Mia saba themanini itaandikwaje kwa tarakimu?",
            "pg008_n0010": "Mstari wa saba. Mia moja kumi na moja itaandikwaje kwa tarakimu?",
            "pg008_n0011": "Mstari wa nane. Mia tisa tisini na tisa itaandikwaje kwa tarakimu?",
            "pg008_n0012": "Swali la 4. Chunguza chati ya namba, kisha jibu swali linalofuata.",
            "pg008_n0013": "Mstari wa kwanza una namba: 16, 30, 102, 940, 20 na 15.",
            "pg008_n0014": "Mstari wa pili una namba: 5, 60, 2, 17, 312 na 72.",
            "pg008_n0015": "Mstari wa tatu una namba: 19, 1, 321, 35, 461 na 966.",
            "pg008_n0017": "5. Andika namba zinazowakilishwa katika mchoro ufuatao.",
        },
        "after": {"pg008_n0017": ["Mamoja. Makumi. Mamia. Maelfu. Makumi elfu. Mchoro una mafungu manne ya mamoja, mafungu matatu ya makumi, mafungu matatu ya mamia, mafungu manne ya maelfu na mafungu matatu ya makumi elfu. Namba hiyo itaandikwaje kwa tarakimu?"]},
    },
    9: {
        "remove": {"pg009_n0006", "pg009_n0007", "pg009_n0008", "pg009_n0009"},
        "replace": {
            "pg009_n0003": "Mfano wa Kwanza",
            "pg009_n0004": "Hesabu au eleza, kisha andika kwa maneno namba inayowakilishwa",
            "pg009_n0011": "1. Hesabu au taja mafungu yenye visanduku 1000. Unapata fungu moja",
            "pg009_n0013": "2. Hesabu au taja mafungu yenye visanduku 100. Unapata mafungu",
            "pg009_n0016": "3. Hesabu au taja mafungu yenye visanduku 10, unapata fungu moja",
            "pg009_n0018": "4. Hesabu au taja visanduku visivyo katika mafungu, unapata visanduku 3.",
        },
        "after": {
            "pg009_n0005": ["Picha inaonesha mafungu ya visanduku katika maelfu, mamia, makumi na mamoja. Maelfu yana fungu moja la visanduku. Mamia yana mafungu mawili ya visanduku. Makumi yana fungu moja la visanduku. Mamoja yana visanduku vitatu."],
        },
    },
    10: {
        "remove": {"pg010_n0006", "pg010_n0007", "pg010_n0008", "pg010_n0009"},
        "replace": {
            "pg010_n0004": "Mfano wa Pili",
            "pg010_n0005": "Hesabu au eleza mafungu ya sarafu, kisha andika namba kwa maneno.",
            "pg010_n0011": "1. Hesabu au taja mafungu yenye maelfu; unapata mafungu tisa",
            "pg010_n0014": "2. Hesabu au taja mafungu ya mamia; unapata mafungu tisa yenye",
            "pg010_n0017": "3. Hesabu au taja mafungu ya makumi; unapata mafungu tisa yenye",
            "pg010_n0020": "4. Hesabu au taja sarafu katika mamoja; unapata mamoja tisa yenye",
        },
        "after": {
            "pg010_n0005": ["Picha inaonesha mafungu ya sarafu katika maelfu, mamia, makumi na mamoja. Maelfu yana mafungu tisa ya sarafu. Mamia yana mafungu tisa ya sarafu. Makumi yana mafungu tisa ya sarafu. Mamoja yana sarafu tisa."],
        },
    },
    11: {
        "replace": {"pg011_n0005": "Zoezi la Pili"},
        "remove": {
            "pg011_n0008", "pg011_n0009", "pg011_n0010", "pg011_n0011",
            "pg011_n0012", "pg011_n0013", "pg011_n0014", "pg011_n0015",
            "pg011_n0016", "pg011_n0017", "pg011_n0018", "pg011_n0019",
            "pg011_n0020", "pg011_n0021", "pg011_n0022", "pg011_n0023",
        },
        "after": {
            "pg011_n0007": [
                "Jedwali la kwanza. Picha inaonesha mafungu ya visanduku katika maelfu, mamia, makumi na mamoja. Maelfu yana mafungu matano ya visanduku. Mamia yana mafungu matatu ya visanduku. Makumi yana mafungu manne ya visanduku. Mamoja yana visanduku sita.",
                "Jedwali la pili. Picha inaonesha mafungu ya penseli katika maelfu, mamia, makumi na mamoja. Maelfu yana mafungu tisa ya penseli. Mamia yana mafungu tisa ya penseli. Makumi yana mafungu sifuri. Mamoja yana penseli tisa.",
            ],
        },
    },
    12: {
        "remove": {"pg012_n0002", "pg012_n0003", "pg012_n0010", "pg012_n0011", "pg012_n0012"},
        "replace": {
            "pg012_n0007": "Mfano wa Kwanza",
            "pg012_n0008": "Angalia jedwali, kisha taja na uandike namba kwa tarakimu",
            "pg012_n0009": "na kwa maneno.",
        },
        "after": {
            "pg012_n0001": ["Picha inaonesha mafungu katika maelfu, mamia, makumi na mamoja. Maelfu yana mafungu sita. Mamia yana mafungu saba. Makumi yana mafungu matano. Mamoja yana vipande tisa."],
            "pg012_n0009": ["Makumi elfu. Maelfu. Mamia. Makumi. Mamoja. Jedwali lina fungu moja la makumi elfu. Safu za maelfu, mamia, makumi na mamoja hazina mafungu; kila moja imeandikwa sifuri."],
        },
    },
    13: {
        "remove": {
            "pg013_n0004", "pg013_n0005", "pg013_n0006",
            "pg013_n0021", "pg013_n0022", "pg013_n0023",
        },
        "replace": {
            "pg013_n0001": "Mfano wa Pili",
            "pg013_n0018": "Mfano wa Tatu",
            "pg013_n0002": "Angalia jedwali, kisha taja na uandike namba kwa",
            "pg013_n0019": "Angalia jedwali, kisha taja na uandike namba kwa",
        },
        "after": {
            "pg013_n0003": ["Picha inaonesha mafungu ya sarafu katika makumi elfu, maelfu, mamia, makumi na mamoja. Makumi elfu yana fungu moja la sarafu. Maelfu, mamia na makumi yana mafungu sifuri. Mamoja yana sarafu moja."],
            "pg013_n0020": ["Picha inaonesha mafungu ya sarafu katika makumi elfu, maelfu, mamia, makumi na mamoja. Makumi elfu yana mafungu matatu ya sarafu. Maelfu yana mafungu mawili ya sarafu. Mamia yana fungu moja la sarafu. Makumi yana mafungu mawili ya sarafu. Mamoja yana sarafu moja."],
        },
    },
    14: {
        "remove": {"pg014_n0020", "pg014_n0021", "pg014_n0022", "pg014_n0023"},
        "replace": {
            "pg014_n0016": "Zoezi la Tatu",
            "pg014_n0018": "1. Hesabu au eleza, kisha andika kwa tarakimu na kwa maneno",
        },
        "after": {
            "pg014_n0019": ["Mchoro a unaonesha mafungu ya sarafu katika makumi elfu, maelfu, mamia, makumi na mamoja. Makumi elfu yana mafungu mawili ya sarafu. Maelfu yana mafungu matano ya sarafu. Mamia yana mafungu manne ya sarafu. Makumi yana mafungu matano ya sarafu. Mamoja yana sarafu sita."],
        },
    },
    15: {"remove": {"pg015_n0002", "pg015_n0003", "pg015_n0004", "pg015_n0005", "pg015_n0006"}, "after": {
        "pg015_n0001": ["Mchoro b unaonesha mafungu ya sarafu katika makumi elfu, maelfu, mamia, makumi na mamoja. Makumi elfu yana mafungu nane ya sarafu. Maelfu yana fungu moja la sarafu. Mamia yana fungu moja la sarafu. Makumi yana mafungu matatu ya sarafu. Mamoja yana sarafu sita."],
        "pg015_n0016": ["Makumi elfu. Maelfu. Mamia. Makumi. Mamoja. Abakasi ina shanga saba za makumi elfu, shanga nne za maelfu, shanga tatu za mamia, shanga tatu za makumi na shanga tano za mamoja."],
    }},
    17: {
        "remove": {
            "pg017_n0005", "pg017_n0006", "pg017_n0007",
            "pg017_n0015", "pg017_n0016", "pg017_n0017", "pg017_n0018", "pg017_n0019",
        },
        "replace": {
            "pg017_n0001": "Mfano wa Kwanza",
            "pg017_n0004": "Jedwali lina nafasi tano. Namba ni elfu ishirini na moja, mia tatu sitini na nne. Kutoka kushoto kwenda kulia: nafasi ya tano ni makumi elfu, ina tarakimu mbili. Nafasi ya nne ni maelfu, ina tarakimu moja. Nafasi ya tatu ni mamia, ina tarakimu tatu. Nafasi ya pili ni makumi, ina tarakimu sita. Nafasi ya kwanza ni mamoja, ina tarakimu nne.",
            "pg017_n0010": "Mfano wa Pili",
            "pg017_n0014": "Jibu. Sehemu a. Namba ni elfu nne mia sita ishirini na nane. Kutoka kulia kwenda kushoto: nane ni mamoja, mbili ni makumi, sita ni mamia, na nne ni maelfu. Sehemu b. Namba ni elfu themanini na tatu na hamsini. Kutoka kulia kwenda kushoto: sifuri ni mamoja, tano ni makumi, sifuri ni mamia, tatu ni maelfu, na nane ni makumi elfu.",
        },
    },
    19: {
        "remove": {
            "pg019_n0009", "pg019_n0011", "pg019_n0013",
            "pg019_n0016", "pg019_n0018", "pg019_n0020", "pg019_n0022",
            "pg019_n0024", "pg019_n0025",
        },
        "replace": {
            "pg019_n0005": "Zoezi la Nne",
            "pg019_n0007": "Swali la kwanza. Andika thamani ya kila tarakimu katika namba zifuatazo.",
            "pg019_n0008": "Sehemu a, 23967. Sehemu b, 76012. Sehemu c, 30645. Sehemu d, 80020.",
            "pg019_n0010": "Swali la pili. Fafanua namba zifuatazo kwa kuzingatia nafasi ya kila tarakimu.",
            "pg019_n0012": "Sehemu a, 40788. Sehemu b, 39615. Sehemu c, 8205. Sehemu d, 98735.",
            "pg019_n0014": "Swali la tatu. Tumia namba zilizoorodheshwa kujaza nafasi zilizo wazi.",
            "pg019_n0015": "Sehemu a. Namba 13739. Makumi elfu, dashi. Maelfu, dashi. Mamia, dashi. Makumi, dashi. Mamoja, dashi.",
            "pg019_n0017": "Sehemu b. Namba 19897. Makumi elfu, dashi. Maelfu, dashi. Mamia, dashi. Makumi, dashi. Mamoja, dashi.",
            "pg019_n0019": "Sehemu c. Namba 39001. Makumi elfu, dashi. Maelfu, dashi. Mamia, dashi. Makumi, dashi. Mamoja, dashi.",
            "pg019_n0021": "Sehemu d. Namba 99678. Makumi elfu, dashi. Maelfu, dashi. Mamia, dashi. Makumi, dashi. Mamoja, dashi.",
            "pg019_n0023": "Swali la nne. Andika namba ambayo tarakimu 7 ipo katika nafasi ya mamia, tarakimu 8 ipo katika nafasi ya mamoja, tarakimu 2 ipo katika nafasi ya maelfu, na tarakimu 8 ipo katika nafasi ya makumi.",
        },
    },
    20: {
        "remove": {"pg020_n0002"},
        "replace": {
            "pg020_n0001": "Swali la tano. Andika thamani ya tarakimu iliyopigiwa mstari katika namba zifuatazo.",
            "pg020_n0003": "Sehemu a. Namba ni elfu tisini na tatu, mia saba arobaini na moja. Namba iliyopigiwa mstari ni ipi? Sehemu b. Namba ni elfu sita na tisini. Namba iliyopigiwa mstari ni ipi? Sehemu c. Namba ni elfu sabini na mbili, mia tisa tisini na nne. Namba iliyopigiwa mstari ni ipi? Sehemu d. Namba ni elfu hamsini, mia moja arobaini na nane. Namba iliyopigiwa mstari ni ipi?",
            "pg020_n0018": "Zoezi la Tano",
        },
    },
    21: {
        "remove": {
            "pg021_n0002", "pg021_n0009", "pg021_n0011",
            "pg021_n0014", "pg021_n0016", "pg021_n0021",
        },
        "replace": {
            "pg021_n0001": "Swali la pili. Soma namba zifuatazo katika jedwali.",
            "pg021_n0003": "Jedwali lina safu ya namba kwa tarakimu na safu ya namba kwa maneno.",
            "pg021_n0004": "Sehemu a. Namba kwa tarakimu ni 38951. Namba hii kwa maneno inatamkwaje?",
            "pg021_n0005": "Sehemu b. Namba kwa tarakimu ni 40690. Namba hii kwa maneno inatamkwaje?",
            "pg021_n0006": "Sehemu c. Namba kwa tarakimu ni 97000. Namba hii kwa maneno inatamkwaje?",
            "pg021_n0007": "Sehemu d. Namba kwa tarakimu ni 30001. Namba hii kwa maneno inatamkwaje?",
            "pg021_n0008": "Swali la tatu. Soma namba zifuatazo zilizoandikwa kwa maneno.",
            "pg021_n0010": "Jedwali lina safu ya namba kwa maneno na safu ya namba kwa tarakimu.",
            "pg021_n0012": "Sehemu a. Sabini elfu mia nane na tano. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0013": "Sehemu b. Tisini na tisa elfu mia nane tisini na nane. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0015": "Sehemu c. Elfu thelathini na tatu mia sita sabini na mbili. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0017": "Sehemu d. Elfu ishirini na moja mia mbili na tano. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0018": "Sehemu e. Tisini elfu na tisa. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0019": "Sehemu f. Elfu hamsini. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0020": "Sehemu g. Sitini na tisa elfu mia moja hamsini na tano. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0022": "Sehemu h. Elfu tisa mia saba hamsini na tatu. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0023": "Sehemu i. Tisini na tisa elfu mia moja tisini na tisa. Namba hii kwa tarakimu inatamkwaje?",
            "pg021_n0024": "Sehemu j. Themanini elfu mia mbili na saba. Namba hii kwa tarakimu inatamkwaje?",
        },
    },
    25: {
        "replace": {
            "pg025_n0013": "Zoezi la Kwanza",
            "pg025_n0015": "Swali la kwanza. Andika mpangilio wenye idadi ya namba tano unaoongezeka",
            "pg025_n0017": "Swali la pili. Andika aina ya mpangilio katika orodha ya namba zifuatazo:",
            "pg025_n0018": "Sehemu a. 4500, 4550, 4600, 4650, 4700, 4750, 4800.",
            "pg025_n0019": "Sehemu b. 58028, 50028, 42028, 34028, 26028, 18028.",
            "pg025_n0020": "Sehemu c. 44013, 54013, 64013, 44013, 54013, 64013, 44013,",
            "pg025_n0022": "Swali la tatu. Orodhesha vitu vitano vilivyopo katika mpangilio",
        },
    },
    26: {
        "remove": {"pg026_n0007_matrix_1", "pg026_n0008_matrix_1", "pg026_n0025_matrix_1"},
        "replace": {
            "pg026_n0004": "Hatua ya kwanza. Taja namba mbili zilizotangulia.",
            "pg026_n0005": "Hatua ya pili. Tafuta tofauti ya namba mbili zilizotangulia.",
            "pg026_n0006": "Hatua ya tatu. Jumlisha tofauti ya namba hizo na namba iliyotangulia.",
            "pg026_n0007": "Mfano wa Kwanza",
            "pg026_n0009": "Mfululizo ni: moja, nne, saba, kumi, kumi na tatu, kumi na sita, kumi na tisa, dashi ya kwanza, dashi ya pili.",
            "pg026_n0011": "Hatua ya kwanza. Namba mbili zilizotangulia ni moja na nne.",
            "pg026_n0012": "Hatua ya pili. Tofauti ni nne kutoa moja, ni sawa na tatu.",
            "pg026_n0013": "Hatua ya tatu. Namba inayofuata katika mpangilio huu inapatikana kwa",
            "pg026_n0014": "kujumlisha tatu kwenye namba iliyotangulia.",
            "pg026_n0015": "Moja jumlisha tatu ni sawa na nne.",
            "pg026_n0016": "Nne jumlisha tatu ni sawa na saba.",
            "pg026_n0017": "Saba jumlisha tatu ni sawa na kumi.",
            "pg026_n0018": "Kumi jumlisha tatu ni sawa na kumi na tatu.",
            "pg026_n0019": "Kumi na tatu jumlisha tatu ni sawa na kumi na sita.",
            "pg026_n0020": "Kumi na sita jumlisha tatu ni sawa na kumi na tisa.",
            "pg026_n0021": "Kumi na tisa jumlisha tatu ni sawa na ishirini na mbili.",
            "pg026_n0022": "Ishirini na mbili jumlisha tatu ni sawa na ishirini na tano.",
            "pg026_n0023": "Kwa hiyo, jibu ni: ishirini na mbili na ishirini na tano.",
            "pg026_n0024": "Mfano wa Pili",
            "pg026_n0026": "Mfululizo ni: mia mbili na moja, mia tatu na mbili, mia nne na tatu, mia tano na nne, dashi ya kwanza, dashi ya pili, dashi ya tatu.",
        },
    },
    27: {
        "replace": {
            "pg027_n0007": "Kwa hiyo, majibu ni: mia sita na tano, mia saba na sita, na mia nane na saba.",
            "pg027_n0008": "Mfano wa Tatu",
        },
        "after": {
            "pg027_n0009": [
                "Mchoro unaonesha mstari wa namba wenye hatua nne zinazoongezeka kwa mia moja.",
                "Mstari unaanzia elfu tano mia moja thelathini na nne. Hatua ya kwanza inaishia kwenye nafasi iliyo wazi. Hatua zinazofuata zinaishia kwenye elfu tano mia tatu thelathini na nne, elfu tano mia nne thelathini na nne, na elfu tano mia tano thelathini na nne.",
                "Namba inayokosekana katika nafasi iliyo wazi ni elfu tano mia mbili thelathini na nne.",
            ],
        },
    },
    28: {
        "replace": {
            "pg028_n0004": "Swali namba kumi. Elfu arobaini na tano mia tano hamsini na mbili, mkato. Elfu arobaini na sita mia tano hamsini na mbili, mkato. Dashi, mkato. Dashi, mkato. Elfu arobaini na tisa mia tano hamsini na mbili, mkato. Elfu hamsini mia tano hamsini na mbili, mkato. Dashi, mkato. Elfu hamsini na mbili mia tano hamsini na mbili.",
            "pg028_n0024": "Kwa hiyo, jibu ni: kumi na tano.",
        },
    },
    30: {
        "replace": {
            "pg030_n0017": "Kwa hiyo, jibu ni: themanini na moja.",
        },
    },
    31: {
        "replace": {
            "pg031_n0003": "Kwa hiyo, jibu ni: sitini na nne.",
            "pg031_n0004": "Zoezi la Nne",
        },
    },
    34: {
        "replace": {
            "pg034_n0002": "Chunguza orodha hii; 4, II, 5, IV, I, III, 2, V, na 3 kisha jibu maswali",
        },
    },
    40: {
        "replace": {
            "pg040_n0001": "Mfano wa Pili",
        },
    },
    42: {
        "remove": {
            "pg042_n0009", "pg042_n0011", "pg042_n0013", "pg042_n0014",
            "pg042_n0016", "pg042_n0024", "pg042_n0026", "pg042_n0028",
        },
        "replace": {
            "pg042_n0015": "Zoezi la Kwanza: Marudio",
            "pg042_n0018": "Swali namba moja. Mia tatu ishirini na saba kuongeza mia nne thelathini na mbili, sawa sawa na ngapi? Swali namba mbili. Mia nane kumi na tisa kuongeza mia moja hamsini, sawa sawa na ngapi?",
            "pg042_n0019": "Swali namba tatu. Mia tano thelathini na sita kuongeza mia mbili thelathini na tano, sawa sawa na ngapi? Swali namba nne. Mia nane arobaini na tano kuongeza mia moja na moja, sawa sawa na ngapi?",
            "pg042_n0020": "Swali namba tano. Mia saba thelathini na tano kuongeza mia mbili thelathini na tano, sawa sawa na ngapi? Swali namba sita. Mia sita arobaini na tano kuongeza mia tatu na kumi na mbili, sawa sawa na ngapi?",
            "pg042_n0021": "Swali namba saba. Mia saba tisini na nane kuongeza mia moja arobaini na tano, sawa sawa na ngapi? Swali namba nane. Mia nane na tano kuongeza thelathini na moja, sawa sawa na ngapi?",
            "pg042_n0022": "Swali namba tisa. Mia tano thelathini na nne kuongeza mia moja na kumi na mbili, sawa sawa na ngapi?",
            "pg042_n0023": "Swali namba kumi. Mia tatu sitini na nne kuongeza mia moja ishirini na tatu, sawa sawa na ngapi? Swali namba kumi na moja. Mia tano thelathini na nne kuongeza mia moja na kumi na tano, sawa sawa na ngapi? Swali namba kumi na mbili. Mia tano arobaini na saba kuongeza mia tatu arobaini na sita, sawa sawa na ngapi?",
            "pg042_n0025": "Swali namba kumi na tatu. Mia saba hamsini na nane kuongeza mia mbili na kumi, sawa sawa na ngapi? Swali namba kumi na nne. Mia tisa na kumi na mbili kuongeza themanini na moja, sawa sawa na ngapi? Swali namba kumi na tano. Mia nne themanini na tano kuongeza mia nne na tatu, sawa sawa na ngapi?",
            "pg042_n0027": "Swali namba kumi na sita. Mia nane themanini na saba kuongeza arobaini, sawa sawa na ngapi? Swali namba kumi na saba. Mia tatu sabini na nne kuongeza mia mbili ishirini na nane, sawa sawa na ngapi? Swali namba kumi na nane. Mia mbili sabini na mbili kuongeza mia tano tisini na saba, sawa sawa na ngapi?",
        },
    },
    43: {
        "remove": {"pg043_n0015", "pg043_n0017", "pg043_n0025"},
        "replace": {
            "pg043_n0010": "Mfano wa Kwanza",
            "pg043_n0012": "Namba ya kwanza ni elfu tano mia mbili arobaini na nane.",
            "pg043_n0013": "Namba ya pili ni elfu moja mia mbili thelathini na moja.",
            "pg043_n0016": "Hatua ya Kwanza. Linganisha namba kwa wima",
            "pg043_n0019": "Hatua ya Pili. Jumlisha mamoja: nane kuongeza moja, sawa sawa na tisa.",
            "pg043_n0020": "Andika tisa katika nafasi ya mamoja.",
            "pg043_n0021": "Jibu la mamoja ni tisa.",
            "pg043_n0022": "Hatua ya Tatu. Jumlisha makumi: nne kuongeza tatu, sawa sawa na saba.",
            "pg043_n0023": "Andika saba katika nafasi ya makumi.",
            "pg043_n0024": "Jibu la makumi na mamoja ni sabini na tisa.",
        },
    },
    44: {
        "remove": {"pg044_n0003", "pg044_n0005"},
        "replace": {
            "pg044_n0001": "Hatua ya Nne. Jumlisha mamia: mbili kuongeza mbili, sawa sawa na nne.",
            "pg044_n0002": "Andika nne katika nafasi ya mamia.",
            "pg044_n0004": "Hatua ya Tano. Jumlisha maelfu: tano kuongeza moja, sawa sawa na sita.",
            "pg044_n0006": "Jibu la mwisho ni elfu sita mia nne sabini na tisa.",
            "pg044_n0007": "Kwa hiyo, jibu ni elfu sita mia nne sabini na tisa.",
            "pg044_n0008": "Mfano wa Pili",
            "pg044_n0010": "Elfu sitini na nane mia tisa arobaini na mbili, kuongeza elfu thelathini na hamsini na moja, sawa sawa na ngapi?",
            "pg044_n0012": "Soma jedwali kutoka chumba cha kulia kwenda chumba cha kushoto. Chumba cha mamoja kina mbili kuongeza moja, jibu ni tatu. Chumba cha makumi kina nne kuongeza tano, jibu ni tisa. Chumba cha mamia kina tisa kuongeza sifuri, jibu ni tisa. Chumba cha maelfu kina nane kuongeza sifuri, jibu ni nane. Chumba cha makumi elfu kina sita kuongeza tatu, jibu ni tisa. Majibu ya vyumba hivyo yanaungana na kuwa elfu tisini na nane mia tisa tisini na tatu.",
            "pg044_n0014": "Hatua ya Kwanza. Jumlisha tarakimu kutoka kulia kuelekea kushoto.",
            "pg044_n0015": "Hatua ya Pili. Jumlisha mamoja: mbili kuongeza moja, sawa sawa na tatu. Andika tatu katika nafasi ya",
            "pg044_n0017": "Hatua ya Tatu. Jumlisha makumi: nne kuongeza tano, sawa sawa na tisa. Andika tisa katika nafasi ya",
            "pg044_n0019": "Hatua ya Nne. Jumlisha mamia: tisa kuongeza sifuri, sawa sawa na tisa. Andika tisa katika nafasi ya",
            "pg044_n0021": "Hatua ya Tano. Jumlisha maelfu: nane kuongeza sifuri, sawa sawa na nane. Andika nane katika nafasi ya",
            "pg044_n0023": "Hatua ya Sita. Jumlisha makumi elfu: sita kuongeza tatu, sawa sawa na tisa. Andika tisa katika nafasi",
            "pg044_n0025": "Kwa hiyo, elfu sitini na nane mia tisa arobaini na mbili, kuongeza elfu thelathini na hamsini na moja, sawa sawa na elfu tisini na nane mia tisa tisini na tatu.",
        },
    },
    45: {
        "remove": {"pg045_n0008", "pg045_n0010", "pg045_n0012", "pg045_n0014"},
        "replace": {
            "pg045_n0001": "Zoezi la Pili",
            "pg045_n0003": "Swali namba moja. Elfu tano mia nne thelathini na tano kuongeza elfu moja mia mbili na nne, sawa sawa na ngapi? Swali namba mbili. Mia sita thelathini na moja kuongeza mia tatu hamsini na saba, sawa sawa na ngapi?",
            "pg045_n0004": "Swali namba tatu. Elfu nne mia sita ishirini na mbili kuongeza elfu nne mia mbili arobaini na tano, sawa sawa na ngapi? Swali namba nne. Elfu ishirini mia mbili na kumi na nane kuongeza elfu tisa mia sita ishirini na moja, sawa sawa na ngapi?",
            "pg045_n0005": "Swali namba tano. Elfu tatu ishirini na tatu kuongeza elfu tano mia tano ishirini na nne, sawa sawa na ngapi? Swali namba sita. Elfu thelathini mia mbili hamsini na moja kuongeza elfu saba arobaini na tatu, sawa sawa na ngapi?",
            "pg045_n0006": "Swali namba saba. Elfu hamsini na tatu mia tisa tisini na tisa kuongeza elfu mbili, sawa sawa na ngapi? Swali namba nane. Elfu sabini na tatu mia nne arobaini na tatu kuongeza elfu sita mia mbili thelathini na sita, sawa sawa na ngapi?",
            "pg045_n0007": "Swali namba tisa. Mpangilio wa wima. Namba ya juu ni elfu sitini na tano mia moja na kumi na nne. Namba ya chini ni elfu ishirini na tatu sabini na tano. Tarakimu za mamoja zinalingana upande wa kulia. Jumlisha namba hizo. Jibu ni ngapi? Swali namba kumi. Mpangilio wa wima. Namba ya juu ni elfu hamsini na saba arobaini na tatu. Namba ya chini ni elfu kumi na mbili mia saba arobaini na nne. Tarakimu za mamoja zinalingana upande wa kulia. Jumlisha namba hizo. Jibu ni ngapi? Swali namba kumi na moja. Mpangilio wa wima. Namba ya juu ni elfu sitini na mbili mia moja hamsini na tisa. Namba ya chini ni elfu ishirini mia nane na kumi. Tarakimu za mamoja zinalingana upande wa kulia. Jumlisha namba hizo. Jibu ni ngapi?",
            "pg045_n0009": "Swali namba kumi na mbili. Mpangilio wa wima. Namba ya juu ni elfu themanini na mbili mia tatu na tano. Namba ya chini ni elfu tano mia mbili na kumi na tatu. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba kumi na tatu. Mpangilio wa wima. Namba ya juu ni elfu hamsini na tisa mia mbili sitini na moja. Namba ya chini ni elfu arobaini mia saba na kumi na mbili. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba kumi na nne. Mpangilio wa wima. Namba ya juu ni elfu themanini na nne mia saba arobaini na tatu. Namba ya chini ni elfu kumi na mbili mia mbili hamsini na moja. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
            "pg045_n0011": "Swali namba kumi na tano. Mpangilio wa wima. Namba ya juu ni elfu hamsini na nne mia saba ishirini na moja. Namba ya chini ni elfu thelathini na tatu mia mbili ishirini na mbili. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba kumi na sita. Mpangilio wa wima. Namba ya juu ni elfu sabini na moja mia mbili thelathini na sita. Namba ya chini ni elfu ishirini na tatu mia nne hamsini na moja. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba kumi na saba. Mpangilio wa wima. Namba ya juu ni elfu hamsini na sita mia saba ishirini na nne. Namba ya chini ni elfu tatu mia moja na kumi na tatu. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
            "pg045_n0013": "Swali namba kumi na nane. Mpangilio wa wima. Namba ya juu ni elfu sabini na tano sabini na mbili. Namba ya chini ni elfu ishirini na mbili na kumi na sita. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba kumi na tisa. Mpangilio wa wima. Namba ya juu ni elfu arobaini na tano mia tano na saba. Namba ya chini ni elfu ishirini na nne mia tatu sitini na mbili. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba ishirini. Mpangilio wa wima. Namba ya juu ni elfu hamsini na sita mia saba na sita. Namba ya chini ni elfu ishirini na tatu mia mbili sabini na tatu. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
        },
    },
    46: {
        "remove": {
            "pg046_n0006", "pg046_n0008", "pg046_n0009", "pg046_n0010", "pg046_n0011", "pg046_n0012", "pg046_n0013",
            "pg046_n0015", "pg046_n0016", "pg046_n0017", "pg046_n0018", "pg046_n0019", "pg046_n0020",
            "pg046_n0022", "pg046_n0023", "pg046_n0024", "pg046_n0025", "pg046_n0026", "pg046_n0027",
            "pg046_n0029", "pg046_n0030", "pg046_n0031", "pg046_n0032", "pg046_n0033",
            "pg046_n0035", "pg046_n0036", "pg046_n0037", "pg046_n0038",
        },
        "replace": {
            "pg046_n0001": "Mfano wa Kwanza",
            "pg046_n0003": "Namba ya juu ni elfu kumi na tatu mia nane ishirini na saba.",
            "pg046_n0004": "Namba ya chini ni elfu kumi na tano mia sita themanini na tano.",
            "pg046_n0005": "Jedwali lina upande wa kushoto wa Hatua na upande wa kulia wa Njia. Kila mstari utasomwa kuanzia Hatua, kisha Njia yake.",
            "pg046_n0007": "Upande wa kushoto. Hatua ya Kwanza. Jumlisha mamoja: saba kuongeza tano, sawa sawa na kumi na mbili. Andika mbili katika nafasi ya mamoja. Badili mamoja kumi kuwa fungu moja la makumi, kisha peleka moja kwenye nafasi ya makumi. Upande wa kulia. Njia. Elfu kumi na tatu mia nane ishirini na saba ipo juu. Elfu kumi na tano mia sita themanini na tano ipo chini. Zimepangwa kwa wima. Baada ya kujumlisha mamoja, tarakimu ya mwisho ya jibu ni mbili, na moja imebebwa kwenda makumi.",
            "pg046_n0014": "Upande wa kushoto. Hatua ya Pili. Jumlisha makumi: moja iliyobebwa, kuongeza mbili, kuongeza nane, sawa sawa na kumi na moja. Andika moja katika nafasi ya makumi. Badili makumi kumi kuwa fungu moja la mamia, kisha peleka moja kwenye nafasi ya mamia. Upande wa kulia. Njia. Mpangilio wa wima unaendelea bila kubadilika. Jibu la muda katika makumi na mamoja ni kumi na mbili, na moja imebebwa kwenda mamia.",
            "pg046_n0021": "Upande wa kushoto. Hatua ya Tatu. Jumlisha mamia: moja iliyobebwa, kuongeza nane, kuongeza sita, sawa sawa na kumi na tano. Andika tano katika nafasi ya mamia. Badili mamia kumi kuwa fungu moja la maelfu, kisha peleka moja kwenye nafasi ya maelfu. Upande wa kulia. Njia. Jibu la muda katika mamia, makumi na mamoja ni mia tano na kumi na mbili, na moja imebebwa kwenda maelfu.",
            "pg046_n0028": "Upande wa kushoto. Hatua ya Nne. Jumlisha maelfu: moja iliyobebwa, kuongeza tatu, kuongeza tano, sawa sawa na tisa. Andika tisa katika nafasi ya maelfu. Upande wa kulia. Njia. Jibu la muda katika maelfu, mamia, makumi na mamoja ni elfu tisa mia tano na kumi na mbili.",
            "pg046_n0034": "Upande wa kushoto. Hatua ya Tano. Jumlisha makumi elfu: moja kuongeza moja, sawa sawa na mbili. Andika mbili katika nafasi ya makumi elfu. Upande wa kulia. Njia. Tarakimu zote zimeunganishwa na kupata elfu ishirini na tisa mia tano na kumi na mbili.",
            "pg046_n0039": "Kwa hiyo, jibu ni elfu ishirini na tisa mia tano na kumi na mbili.",
        },
    },
    47: {
        "remove": {
            "pg047_n0007", "pg047_n0008", "pg047_n0009", "pg047_n0010",
            "pg047_n0012", "pg047_n0013", "pg047_n0014", "pg047_n0015", "pg047_n0016", "pg047_n0017",
            "pg047_n0019", "pg047_n0020", "pg047_n0021", "pg047_n0022",
            "pg047_n0024", "pg047_n0025", "pg047_n0026", "pg047_n0027", "pg047_n0028",
            "pg047_n0030", "pg047_n0031", "pg047_n0032", "pg047_n0033",
        },
        "replace": {
            "pg047_n0001": "Mfano wa Pili",
            "pg047_n0003": "Namba ya juu ni elfu thelathini na moja sabini na mbili.",
            "pg047_n0004": "Namba ya chini ni elfu ishirini na tisa mia nane hamsini na tatu.",
            "pg047_n0005": "Jedwali lina upande wa kushoto wa Hatua na upande wa kulia wa Njia. Kila mstari utasomwa kuanzia Hatua, kisha Njia yake.",
            "pg047_n0006": "Upande wa kushoto. Hatua ya Kwanza. Jumlisha mamoja: mbili kuongeza tatu, sawa sawa na tano. Andika tano katika nafasi ya mamoja. Upande wa kulia. Njia. Namba zimepangwa kwa wima. Tarakimu ya mamoja katika jibu ni tano.",
            "pg047_n0011": "Upande wa kushoto. Hatua ya Pili. Jumlisha makumi: saba kuongeza tano, sawa sawa na kumi na mbili. Andika mbili katika nafasi ya makumi. Badili makumi kumi kuwa fungu moja la mamia, kisha peleka moja kwenye nafasi ya mamia. Upande wa kulia. Njia. Jibu la muda katika makumi na mamoja ni ishirini na tano, na moja imebebwa kwenda mamia.",
            "pg047_n0018": "Upande wa kushoto. Hatua ya Tatu. Jumlisha mamia: moja iliyobebwa, kuongeza sifuri, kuongeza nane, sawa sawa na tisa. Andika tisa katika nafasi ya mamia. Upande wa kulia. Njia. Jibu la muda katika mamia, makumi na mamoja ni mia tisa ishirini na tano.",
            "pg047_n0023": "Upande wa kushoto. Hatua ya Nne. Jumlisha maelfu: moja kuongeza tisa, sawa sawa na kumi. Andika sifuri katika nafasi ya maelfu. Badili maelfu kumi kuwa fungu moja la makumi elfu, kisha peleka moja kwenye nafasi ya makumi elfu. Upande wa kulia. Njia. Nafasi ya maelfu ina sifuri; sehemu ya jibu iliyopatikana hadi sasa ni sifuri, mia tisa ishirini na tano.",
            "pg047_n0029": "Upande wa kushoto. Hatua ya Tano. Jumlisha makumi elfu: moja iliyobebwa, kuongeza tatu, kuongeza mbili, sawa sawa na sita. Andika sita katika nafasi ya makumi elfu. Upande wa kulia. Njia. Tarakimu zote zimeunganishwa na kupata elfu sitini mia tisa ishirini na tano.",
            "pg047_n0034": "Kwa hiyo, jibu ni elfu sitini mia tisa ishirini na tano.",
        },
    },
    48: {
        "remove": {"pg048_n0005"},
        "replace": {
            "pg048_n0001": "Mfano wa Tatu",
            "pg048_n0003": "Elfu hamsini na nane mia mbili sabini na moja, kuongeza elfu thelathini na mbili mia tisa themanini na tisa, sawa sawa na ngapi?",
            "pg048_n0004": "Njia. Mchoro unaonesha namba mbili katika mpangilio wa ulalo. Kila tarakimu imeunganishwa na nafasi yake katika jibu, kuanzia mamoja upande wa kulia hadi makumi elfu upande wa kushoto.",
            "pg048_n0006": "Namba ya kwanza ni elfu hamsini na nane mia mbili sabini na moja. Namba ya pili ni elfu thelathini na mbili mia tisa themanini na tisa. Alama ya kuongeza iko katikati. Jibu ni elfu tisini na moja mia mbili sitini. Namba moja imebebwa kutoka mamoja kwenda makumi, kutoka makumi kwenda mamia, kutoka mamia kwenda maelfu, na kutoka maelfu kwenda makumi elfu.",
            "pg048_n0008": "Hatua ya Kwanza. Jumlisha tarakimu kuanzia kulia kuelekea kushoto.",
            "pg048_n0009": "Hatua ya Pili. Jumlisha mamoja: moja kuongeza tisa, sawa sawa na kumi. Andika sifuri katika nafasi ya",
            "pg048_n0010": "mamoja. Badili mamoja kumi kuwa fungu moja la makumi. Peleka moja",
            "pg048_n0011": "kwenye nafasi ya makumi.",
            "pg048_n0012": "Hatua ya Tatu. Jumlisha makumi: moja iliyobebwa, kuongeza saba, kuongeza nane, sawa sawa na kumi na sita. Andika sita katika nafasi ya",
            "pg048_n0013": "makumi. Badili makumi kumi kuwa fungu moja la mamia. Peleka moja",
            "pg048_n0015": "Hatua ya Nne. Jumlisha mamia: moja iliyobebwa, kuongeza mbili, kuongeza tisa, sawa sawa na kumi na mbili. Andika mbili katika nafasi ya",
            "pg048_n0016": "mamia. Badili mamia kumi kuwa fungu moja la maelfu. Peleka moja",
            "pg048_n0018": "Hatua ya Tano. Jumlisha maelfu: moja iliyobebwa, kuongeza nane, kuongeza mbili, sawa sawa na kumi na moja. Andika moja katika nafasi",
            "pg048_n0019": "ya maelfu. Badili maelfu kumi kuwa fungu moja la makumi elfu. Peleka",
            "pg048_n0021": "Hatua ya Sita. Jumlisha makumi elfu: moja iliyobebwa, kuongeza tano, kuongeza tatu, sawa sawa na tisa. Andika tisa katika nafasi",
            "pg048_n0023": "Kwa hiyo, jibu ni elfu tisini na moja mia mbili sitini.",
        },
    },
    49: {
        "remove": {"pg049_n0009", "pg049_n0011", "pg049_n0013", "pg049_n0015"},
        "replace": {
            "pg049_n0001": "Zoezi la Tatu",
            "pg049_n0003": "Swali namba 1. Namba 53415 kuongeza 21045, sawa sawa na ngapi? Swali namba 2. Namba 64124 kuongeza 16283, sawa sawa na ngapi?",
            "pg049_n0004": "Swali namba 3. Namba 75520 kuongeza 9221, sawa sawa na ngapi? Swali namba 4. Namba 66612 kuongeza 24588, sawa sawa na ngapi?",
            "pg049_n0005": "Swali namba 5. Namba 48434 kuongeza 23537, sawa sawa na ngapi? Swali namba 6. Namba 67456 kuongeza 11553, sawa sawa na ngapi?",
            "pg049_n0006": "Swali namba 7. Namba 53656 kuongeza 6667, sawa sawa na ngapi? Swali namba 8. Namba 59816 kuongeza 32275, sawa sawa na ngapi?",
            "pg049_n0007": "Swali namba 9. Namba 43892 kuongeza 8329, sawa sawa na ngapi? Swali namba 10. Namba 77999 kuongeza 10001, sawa sawa na ngapi?",
            "pg049_n0008": "Swali namba 11. Mpangilio wa wima. Namba ya juu ni 57336. Namba ya chini ni 12217. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba 12. Mpangilio wa wima. Namba ya juu ni 55376. Namba ya chini ni 21206. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba 13. Mpangilio wa wima. Namba ya juu ni 81858. Namba ya chini ni 12141. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
            "pg049_n0010": "Swali namba 14. Mpangilio wa wima. Namba ya juu ni 64599. Namba ya chini ni 16433. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba 15. Mpangilio wa wima. Namba ya juu ni 48879. Namba ya chini ni 22300. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba 16. Mpangilio wa wima. Namba ya juu ni 48289. Namba ya chini ni 3457. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
            "pg049_n0012": "Swali namba 17. Mpangilio wa wima. Namba ya juu ni 61823. Namba ya chini ni 27278. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba 18. Mpangilio wa wima. Namba ya juu ni 87735. Namba ya chini ni 5486. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi? Swali namba 19. Mpangilio wa wima. Namba ya juu ni 85519. Namba ya chini ni 2791. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
            "pg049_n0014": "Swali namba 20. Mpangilio wa wima. Namba ya juu ni 18702. Namba ya chini ni 79308. Pangilia mamoja upande wa kulia, kisha jumlisha. Jibu ni ngapi?",
            "pg049_n0017": "Mfano wa Kwanza",
        },
    },
    52: {
        "remove": {"pg052_n0016", "pg052_n0018", "pg052_n0020", "pg052_n0022"},
        "replace": {
            "pg052_n0010": "Zoezi la Kwanza: Marudio",
            "pg052_n0012": "Swali namba 1. Namba 536 kutoa 111, sawa sawa na ngapi? Swali namba 2. Namba 935 kutoa 235, sawa sawa na ngapi?",
            "pg052_n0013": "Swali namba 3. Namba 945 kutoa 633, sawa sawa na ngapi? Swali namba 4. Namba 708 kutoa 455, sawa sawa na ngapi?",
            "pg052_n0014": "Swali namba 5. Namba 798 kutoa 455, sawa sawa na ngapi? Swali namba 6. Namba 845 kutoa 101, sawa sawa na ngapi?",
            "pg052_n0015": "Swali namba 7. Mpangilio wa wima. Namba ya juu ni 348. Namba ya chini ni 230. Pangilia mamoja upande wa kulia, kisha toa namba ya chini kutoka namba ya juu. Jibu ni ngapi? Swali namba 8. Mpangilio wa wima. Namba ya juu ni 789. Namba ya chini ni 255. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 9. Mpangilio wa wima. Namba ya juu ni 567. Namba ya chini ni 246. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg052_n0017": "Swali namba 10. Mpangilio wa wima. Namba ya juu ni 659. Namba ya chini ni 185. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 11. Mpangilio wa wima. Namba ya juu ni 690. Namba ya chini ni 562. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 12. Mpangilio wa wima. Namba ya juu ni 876. Namba ya chini ni 643. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg052_n0019": "Swali namba 13. Mpangilio wa wima. Namba ya juu ni 619. Namba ya chini ni 51. Namba ya chini ina tarakimu mbili, hivyo nafasi ya mamia iko wazi. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 14. Mpangilio wa wima. Namba ya juu ni 819. Namba ya chini ni 150. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 15. Mpangilio wa wima. Namba ya juu ni 328. Namba ya chini ni 226. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg052_n0021": "Swali namba 16. Mpangilio wa wima. Namba ya juu ni 422. Namba ya chini ni 123. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 17. Mpangilio wa wima. Namba ya juu ni 505. Namba ya chini ni 146. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 18. Mpangilio wa wima. Namba ya juu ni 862. Namba ya chini ni 672. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
        },
    },
    91: {
        "replace": {
            "pg091_n0013": "Zoezi la Kwanza: Marudio",
        },
        "remove": {"pg091_n0016", "pg091_n0017"},
        "after": {
            "pg091_n0015": ["Umbo a lina maduara matatu, na duara moja limetiwa kivuli. Sehemu iliyotiwa kivuli ni theluthi moja. Umbo b ni duara lililogawanywa katika sehemu nne sawa, na sehemu moja imetiwa kivuli. Sehemu iliyotiwa kivuli ni robo moja. Umbo c ni duara lililogawanywa katika sehemu tatu sawa, na sehemu moja imetiwa kivuli. Sehemu iliyotiwa kivuli ni theluthi moja. Umbo d ni mstatili uliogawanywa katika sehemu mbili sawa, na sehemu moja imetiwa kivuli. Sehemu iliyotiwa kivuli ni nusu."],
        },
    },
    172: {"after": {"pg172_n0002": [
        "Umbo namba moja ni mstatili. Urefu wake ni mita kumi na tisa. Upana wake ni mita saba.",
        "Umbo namba mbili ni mraba. Kila upande una urefu wa mita nane.",
        "Umbo namba tatu ni mraba. Kila upande una urefu wa mita kumi na mbili.",
        "Umbo namba nne ni pembetatu. Pande zake zina urefu wa sentimita tisa, sentimita saba na sentimita kumi na nane.",
        "Umbo namba tano ni pembetatu. Pande zake zina urefu wa sentimita tisa, sentimita tisa na sentimita kumi na moja.",
        "Umbo namba sita ni mraba. Kila upande una urefu wa mita kumi.",
        "Umbo namba saba ni mstatili. Urefu wake ni sentimita thelathini na mbili. Upana wake ni sentimita kumi na tatu.",
        "Umbo namba nane ni pembetatu. Pande zake zina urefu wa sentimita sita, sentimita nane na sentimita kumi na mbili.",
    ]}},
    179: {"after": {"pg179_n0014": [
        "Jedwali lina aina tano za matunda. Majina ya matunda ni mananasi, ndizi, matufaha, machungwa na embe.",
        "Mananasi ni matano. Ndizi ni nne. Matufaha ni manne. Machungwa ni manne. Embe ni moja. Jumla ya matunda yote ni kumi na nane.",
    ]}},
    180: {
        "replace": {"pg180_n0002": "1. Chora au tenga makundi ya matunda yanayofanana."},
        "after": {"pg180_n0014": [
            "Jedwali lina safu tatu. Safu ya kwanza ina jina la chombo. Safu ya pili ina idadi ya vyombo kwa picha. Safu ya tatu ina idadi ya vyombo kwa tarakimu.",
            "Mstari wa kwanza una bilauri. Kuna picha tatu za bilauri. Idadi kwa tarakimu ni tatu. Mstari wa pili una sufuria. Kuna picha mbili za sufuria. Idadi kwa tarakimu ni mbili.",
        ]},
    },
    181: {
        "remove": {"pg181_n0013", "pg181_n0014"},
        "after": {
            "pg181_n0005": [
                "Huu ni mwendelezo wa jedwali la vyombo kutoka ukurasa uliopita.",
                "Mstari wa vikombe una picha nne za vikombe. Idadi kwa tarakimu ni nne. Mstari wa vijiko una picha kumi za vijiko. Idadi kwa tarakimu ni kumi.",
            ],
            "pg181_n0012": [
                "Jedwali la juu lina safu nne za miaka na idadi ya miti iliyopandwa.",
                "Mwaka elfu mbili na kumi na mbili, idadi ya miti ni kumi. Mwaka elfu mbili na kumi na tatu, idadi ya miti ni minane. Mwaka elfu mbili na kumi na nne, idadi ya miti ni sita. Mwaka elfu mbili na kumi na tano, idadi ya miti ni kumi na miwili.",
                "Chini yake kuna takwimu kwa picha. Takwimu hizi zinaanzia ukurasa huu na zinaendelea katika ukurasa unaofuata.",
                "Safu ya mwaka elfu mbili na kumi na mbili ina picha kumi za miti. Hivyo, idadi ya miti ni kumi.",
            ],
        },
    },
    182: {"after": {"pg182_n0004": [
        "Huu ni mwendelezo wa jedwali la picha za miti.",
        "Safu ya mwaka elfu mbili na kumi na tatu ina picha nane za miti. Hivyo, idadi ya miti ni minane.",
        "Safu ya mwaka elfu mbili na kumi na nne ina picha sita za miti. Hivyo, idadi ya miti ni sita.",
        "Safu ya mwaka elfu mbili na kumi na tano ina picha kumi na mbili za miti. Hivyo, idadi ya miti ni kumi na miwili.",
    ]}},
    183: {
        "replace": {
            "pg183_n0001": "Mfano wa kwanza",
            "pg183_n0010": "Hatua ya kwanza. Takwimu kwa picha hapo juu inaonesha aina tatu za mifugo:",
            "pg183_n0011": "ng'ombe, mbuzi na mbwa.",
            "pg183_n0012": "Hatua ya pili. Jibu.",
            "pg183_n0013": "Tafsiri ya takwimu hizo ni kama ifuatavyo:",
            "pg183_n0014": "Sehemu a. Idadi ya ng'ombe ni nne.",
            "pg183_n0015": "Sehemu b. Idadi ya mbuzi ni minane.",
            "pg183_n0016": "Sehemu c. Idadi ya mbwa ni mbili.",
        },
        "after": {"pg183_n0004": [
            "Jedwali lina mistari mitatu ya mifugo.",
            "Mstari wa kwanza una picha nne za ng'ombe. Mstari wa pili una picha nane za mbuzi. Mstari wa tatu una picha mbili za mbwa.",
        ]},
    },
    184: {"replace": {
        "pg184_n0001": "Mfano wa pili",
        "pg184_n0005": "Kipimio: picha moja ya gunia inawakilisha magunia elfu moja.",
        "pg184_n0006": "Jedwali lina aina ya zao na idadi ya magunia kwa tarakimu.",
        "pg184_n0007": "Mahindi yana magunia elfu ishirini na tano.",
        "pg184_n0008": "Maharage yana magunia elfu kumi na nne.",
        "pg184_n0009": "Viazi vina magunia elfu thelathini.",
        "pg184_n0010": "Mtama una magunia elfu nane.",
        "pg184_n0018": "Mahindi yana picha ishirini na tano za magunia. Picha hizo zinawakilisha magunia elfu ishirini na tano.",
        "pg184_n0019": "Maharage yana picha kumi na nne za magunia. Picha hizo zinawakilisha magunia elfu kumi na nne.",
    }},
    185: {"replace": {
        "pg185_n0001": "Mwendelezo wa jedwali. Viazi vina picha thelathini za magunia. Picha hizo zinawakilisha magunia elfu thelathini.",
        "pg185_n0002": "Mtama una picha nane za magunia. Picha hizo zinawakilisha magunia elfu nane.",
        "pg185_n0003": "Zoezi la Pili",
    }},
}


def source(page):
    path = ROOT / f"pg{page:03d}_sec001.html"
    raw = path.read_text(encoding="utf-8")
    block = re.search(r'<div class="accessible-transcript[^>]*>(.*?)</div>', raw, re.S).group(1)
    nodes = [(node_id, html.unescape(re.sub(r"<[^>]+>", "", text)).strip()) for node_id, text in re.findall(r'data-id="([^"]+)"[^>]*>(.*?)</span>', block, re.S) if "_matrix_" not in node_id]
    while nodes and (re.fullmatch(r"\d+", nodes[-1][1]) or ".indd" in nodes[-1][1]):
        nodes.pop()
    words = [(int(i), html.unescape(re.sub(r"<[^>]+>", "", text)).strip()) for i, text in re.findall(r'<span class="pdf-word" data-word-index="(\d+)"[^>]*>(.*?)</span>', raw, re.S)]
    return path, raw, nodes, words


def norm(value):
    return re.sub(r"[^a-z0-9\u00c0-\u024f]+", "", value.lower())


def map_words(cues, words):
    normalized = [norm(text) for _, text in words]
    cursor = 0
    last = words[0][0] if words else 0
    for cue in cues:
        needle = norm(cue["text"])
        found = next((i for i in range(cursor, len(words)) if normalized[i] == needle), -1)
        if found >= 0:
            last, cursor = words[found][0], found + 1
        cue["sourceIndex"] = last


def patch_transcript(raw, replacements, after, remove=()):
    for node_id in remove:
        raw = re.sub(rf'\s*<span data-id="{re.escape(node_id)}">.*?</span>', "", raw, count=1, flags=re.S)
    for node_id, replacement in replacements.items():
        pattern = rf'(<span data-id="{re.escape(node_id)}">)(.*?)(</span>)'
        raw = re.sub(pattern, lambda m: m.group(1) + html.escape(replacement) + m.group(3), raw, count=1, flags=re.S)
    for node_id, additions in after.items():
        pattern = rf'(<span data-id="{re.escape(node_id)}">.*?</span>)'
        stale = rf'\s*<span data-id="{re.escape(node_id)}_matrix_\d+">.*?</span>'
        raw = re.sub(stale, "", raw, flags=re.S)
        extras = "".join(
            f' <span data-id="{node_id}_matrix_{i+1}">{html.escape(text)}</span>'
            for i, text in enumerate(additions)
        )
        raw = re.sub(pattern, lambda m: m.group(1) + extras, raw, count=1, flags=re.S)
    return raw


async def generate(page, timecodes):
    import edge_tts
    from fix_full_book_audio import number_to_swahili, roman_to_int

    cfg = CONFIG[page]
    path, raw, nodes, words = source(page)
    replacements, after = cfg.get("replace", {}), cfg.get("after", {})
    segments = []
    for node_id, original in nodes:
        if node_id in cfg.get("remove", set()):
            continue
        segment_text = replacements.get(node_id, original)
        if page == 34:
            segment_text = re.sub(
                r"(?<![A-Za-z])([IVXLCDM]+)(?![A-Za-z])",
                lambda match: f"{number_to_swahili(roman_to_int(match.group(1)))} ya Kirumi",
                segment_text,
            )
        if page in {49, 52}:
            segment_text = re.sub(
                r"(?<!\d)(\d+)(?!\d)",
                lambda match: number_to_swahili(int(match.group(1))),
                segment_text,
            )
        segments.append((segment_text, "source"))
        for extra in after.get(node_id, []):
            kind = "table" if page == 7 and node_id == "pg007_n0012" else "image"
            segments.append((extra, kind))
    text = " ".join(value for value, _ in segments)
    cues = []
    audio_name = f"page-{page:03d}-matrix-v12.mp3"
    output = ROOT / "content" / "rehema"
    audio_path = output / audio_name
    temp_path = output / f".{audio_name}.tmp"
    with temp_path.open("wb") as audio:
        page_rate = "-20%" if 8 <= page <= 15 or page == 17 else RATE
        stream = edge_tts.Communicate(
            text, VOICE, rate=page_rate, boundary="WordBoundary",
            connect_timeout=15, receive_timeout=90,
        )
        iterator = stream.stream().__aiter__()
        while True:
            try:
                event = await asyncio.wait_for(iterator.__anext__(), timeout=60)
            except StopAsyncIteration:
                break
            except TimeoutError:
                expected_tail = [norm(token) for token in text.split() if norm(token)][-3:]
                actual_tail = [norm(cue["text"]) for cue in cues if norm(cue["text"])][-3:]
                if cues and audio.tell() >= 1000 and actual_tail == expected_tail:
                    break
                raise
            if event["type"] == "audio":
                audio.write(event["data"])
            elif event["type"] == "WordBoundary":
                start = event["offset"] / 10_000_000
                duration = event["duration"] / 10_000_000
                cues.append({"text": event["text"], "start": round(start, 6), "end": round(start + duration, 6)})
    temp_path.replace(audio_path)
    map_words(cues, words)
    if page == 7:
        heading = ["zoezi", "la", "kwanza", "marudio"]
        normalized_cues = [norm(cue["text"]) for cue in cues]
        for start in range(len(cues) - len(heading) + 1):
            if normalized_cues[start:start + len(heading)] == heading:
                for offset, source_index in enumerate((56, 57, 58, 59)):
                    cues[start + offset]["sourceIndex"] = source_index
                break
    if page == 8:
        visual_phrases = {
            "q3": "Andika namba zifuatazo kwa tarakimu Mstari wa kwanza na wa pili ni mfano",
            "q4": "Chunguza chati ya namba kisha jibu swali linalofuata",
            "q5": "Andika namba zinazowakilishwa katika mchoro ufuatao",
        }
        normalized_cues = [norm(cue["text"]) for cue in cues]
        for class_name, phrase in visual_phrases.items():
            tokens = [norm(token) for token in phrase.split()]
            for start in range(len(cues) - len(tokens) + 1):
                if normalized_cues[start:start + len(tokens)] == tokens:
                    for offset in range(len(tokens)):
                        cues[start + offset]["targetSelector"] = f".{class_name} .matrix-highlight-word:nth-of-type({offset + 2})"
                    break
    if page == 9:
        normalized_cues = [norm(cue["text"]) for cue in cues]
        visual_phrases = {
            "example-instruction-patch": "Hesabu au eleza kisha andika kwa maneno namba inayowakilishwa na visanduku vifuatavyo",
            "step1": "Hesabu au taja mafungu yenye visanduku 1000 Unapata fungu moja lenye visanduku 1000",
            "step2": "Hesabu au taja mafungu yenye visanduku 100 Unapata mafungu mawili yenye visanduku 100 kila fungu visanduku 100 + visanduku 100 visanduku 200",
            "step3": "Hesabu au taja mafungu yenye visanduku 10 unapata fungu moja lenye visanduku 10",
            "step4": "Hesabu au taja visanduku visivyo katika mafungu unapata visanduku 3",
        }
        for class_name, phrase in visual_phrases.items():
            tokens = [norm(token) for token in phrase.split()]
            for start in range(len(cues) - len(tokens) + 1):
                if normalized_cues[start:start + len(tokens)] == tokens:
                    for offset in range(len(tokens)):
                        visual_index = offset + 1
                        if class_name == "step2" and offset >= 20:
                            visual_index += 1
                        cues[start + offset]["targetSelector"] = f".{class_name} .matrix-highlight-word:nth-of-type({visual_index})"
                    break
        step5_start = next((i for i, cue in enumerate(cues) if norm(cue["text"]) == "jumlisha"), None)
        if step5_start is not None:
            for offset in range(16):
                cues[step5_start + offset]["targetSelector"] = f".step5 .matrix-highlight-word:nth-of-type({offset + 1})"
            cues[step5_start + 16]["targetSelector"] = ".step5 .matrix-highlight-word:nth-of-type(17)"
            cues[step5_start + 17]["targetSelector"] = ".step5 .matrix-highlight-word:nth-of-type(27)"
        step6_start = next((i for i, cue in enumerate(cues) if norm(cue["text"]) == "tarakimu" and i > 100), None)
        if step6_start is not None:
            for offset in range(min(20, len(cues) - step6_start)):
                cues[step6_start + offset]["targetSelector"] = f".step6 .matrix-highlight-word:nth-of-type({offset + 1})"
    if page == 10:
        normalized_cues = [norm(cue["text"]) for cue in cues]
        intro_tokens = [norm(token) for token in "Hesabu au eleza mafungu ya sarafu kisha andika namba kwa maneno".split()]
        for start in range(len(cues) - len(intro_tokens) + 1):
            if normalized_cues[start:start + len(intro_tokens)] == intro_tokens:
                for offset in range(len(intro_tokens)):
                    cues[start + offset]["targetSelector"] = f".example2-instruction-patch .matrix-highlight-word:nth-of-type({offset + 1})"
                break
        visible_steps = [
            "Hesabu au taja mafungu yenye maelfu; unapata mafungu tisa yenye 1000 kila moja. Sawa na; 1000 + 1000 + 1000 + 1000 + 1000 + 1000 + 1000 + 1000 + 1000 = 9000.",
            "Hesabu au taja mafungu ya mamia; unapata mafungu tisa yenye 100 kila moja. Hii ni sawa na; 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 + 100 = 900.",
            "Hesabu au taja mafungu ya makumi; unapata mafungu tisa yenye sarafu 10 kila moja, ambazo ni; 10 + 10 + 10 + 10 + 10 + 10 + 10 + 10 + 10 = 90.",
            "Hesabu au taja sarafu katika mamoja; unapata mamoja tisa yenye sarafu 1 kila moja. Hii inakuwa; 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 = 9.",
        ]
        starts = [i for i, cue in enumerate(cues) if norm(cue["text"]) == "hesabu"][-4:]
        for step_number, start in enumerate(starts, 1):
            end = starts[step_number] if step_number < len(starts) else len(cues)
            visual_norms = [norm(token) for token in visible_steps[step_number - 1].split()]
            visual_pos = 0
            for cue_index in range(start, end):
                cue_norm = normalized_cues[cue_index]
                if not cue_norm:
                    continue
                match = next((i for i in range(visual_pos, len(visual_norms)) if visual_norms[i] == cue_norm), None)
                if match is None:
                    continue
                cues[cue_index]["targetSelector"] = f".step{step_number} .matrix-highlight-word:nth-of-type({match + 1})"
                visual_pos = match + 1
    if page == 12:
        phrase = "Angalia jedwali kisha taja na uandike namba kwa tarakimu na kwa maneno"
        tokens = [norm(token) for token in phrase.split()]
        normalized_cues = [norm(cue["text"]) for cue in cues]
        for start in range(len(cues) - len(tokens) + 1):
            if normalized_cues[start:start + len(tokens)] == tokens:
                for offset in range(len(tokens)):
                    cues[start + offset]["targetSelector"] = f".inclusive-instruction-patch .matrix-highlight-word:nth-of-type({offset + 1})"
                break
    if page == 13:
        phrase = "Angalia jedwali kisha taja na uandike namba kwa tarakimu na kwa maneno"
        tokens = [norm(token) for token in phrase.split()]
        normalized_cues = [norm(cue["text"]) for cue in cues]
        occurrence = 0
        for start in range(len(cues) - len(tokens) + 1):
            if normalized_cues[start:start + len(tokens)] == tokens:
                occurrence += 1
                class_name = f"instruction{occurrence}"
                for offset in range(len(tokens)):
                    cues[start + offset]["targetSelector"] = f".{class_name} .matrix-highlight-word:nth-of-type({offset + 1})"
                if occurrence == 2:
                    break
    if page == 14:
        phrase = "Hesabu au eleza kisha andika kwa tarakimu na kwa maneno namba inayowakilishwa na michoro ifuatayo"
        tokens = [norm(token) for token in phrase.split()]
        normalized_cues = [norm(cue["text"]) for cue in cues]
        for start in range(len(cues) - len(tokens) + 1):
            if normalized_cues[start:start + len(tokens)] == tokens:
                for offset in range(len(tokens)):
                    cues[start + offset]["targetSelector"] = f".question1-patch .matrix-highlight-word:nth-of-type({offset + 1})"
                break
    offset = 0
    for value, segment_kind in segments:
        count = len(re.findall(r"\S+", value))
        part = cues[offset:offset + count]
        if segment_kind == "image":
            for cue in part:
                cue.pop("sourceIndex", None)
                cue["targetImage"] = True
        elif segment_kind == "table":
            row_indexes = {"86": 91, "39": 95, "475": 97, "884": 99, "706": 101, "912": 103}
            active = 75
            for cue in part:
                token = cue["text"].strip(".,;:!?")
                if token in row_indexes:
                    active = row_indexes[token]
                elif active == 91 and norm(token) == "themanini":
                    active = 92
                elif active in (92, 93) and norm(token) == "na":
                    active = 93
                elif active in (92, 93) and norm(token) == "sita":
                    active = 94
                cue["sourceIndex"] = active
        offset += count
    entry = {"audio": audio_name, "voice": VOICE, "rate": 0.8 if 8 <= page <= 15 or page == 17 else 0.9, "pitch": "neutral", "version": 27, "words": cues}
    (output / f"page-{page:03d}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    timecodes[str(page)] = entry
    path.write_text(patch_transcript(raw, replacements, after, cfg.get("remove", set())), encoding="utf-8")
    print(f"page={page} words={len(cues)} audio={audio_name}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcripts-only", action="store_true")
    parser.add_argument("--page", type=int)
    args = parser.parse_args()
    timecodes_path = ROOT / "content" / "rehema" / "timecodes.json"
    timecodes = json.loads(timecodes_path.read_text(encoding="utf-8"))
    if args.transcripts_only:
        selected = CONFIG.items() if args.page is None else [(args.page, CONFIG[args.page])]
        for page, cfg in selected:
            path, raw, _, _ = source(page)
            updated = patch_transcript(raw, cfg.get("replace", {}), cfg.get("after", {}), cfg.get("remove", set()))
            path.write_text(updated, encoding="utf-8")
            print(f"page={page} transcript=updated")
        return
    selected_pages = CONFIG if args.page is None else [args.page]
    for page in selected_pages:
        await generate(page, timecodes)
    timecodes_path.write_text(json.dumps(timecodes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())

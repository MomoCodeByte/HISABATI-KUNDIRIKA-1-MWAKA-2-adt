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
        "remove": {"pg020_n0002", "pg020_n0012"},
        "replace": {
            "pg020_n0001": "Swali namba tano. Andika thamani ya tarakimu iliyopigiwa mstari katika namba zifuatazo.",
            "pg020_n0003": "Sehemu a. Namba ni elfu tisini na tatu, mia saba arobaini na moja. Tarakimu iliyopigiwa mstari ni saba. Sehemu b. Namba ni elfu sita na tisini. Tarakimu iliyopigiwa mstari ni tisa. Sehemu c. Namba ni elfu sabini na mbili, mia tisa tisini na nne. Tarakimu iliyopigiwa mstari ni saba. Sehemu d. Namba ni elfu hamsini, mia moja arobaini na nane. Tarakimu iliyopigiwa mstari ni sifuri.",
            "pg020_n0009": "Sehemu a, elfu moja na moja. Sehemu b, kumi na tisa elfu. Sehemu c, tisini na tisa elfu mia tisa tisini na tisa. Sehemu d, elfu kumi na saba. Sehemu e, sabini na tatu elfu na nane.",
            "pg020_n0010": "Jibu. Soma jedwali mstari kwa mstari.",
            "pg020_n0011": "Jedwali lina safu ya Namba kwa tarakimu na safu ya Namba kwa maneno.",
            "pg020_n0013": "Mstari a. Namba kwa tarakimu ni elfu moja na moja. Namba kwa maneno ni elfu moja na moja.",
            "pg020_n0014": "Mstari b. Namba kwa tarakimu ni elfu kumi na tisa. Namba kwa maneno ni kumi na tisa elfu.",
            "pg020_n0015": "Mstari c. Namba kwa tarakimu ni elfu tisini na tisa mia tisa tisini na tisa. Namba kwa maneno ni tisini na tisa elfu mia tisa tisini na tisa.",
            "pg020_n0016": "Mstari d. Namba kwa tarakimu ni elfu kumi na saba. Namba kwa maneno ni kumi elfu na saba.",
            "pg020_n0017": "Mstari e. Namba kwa tarakimu ni elfu sabini na tatu na nane. Namba kwa maneno ni sabini na tatu elfu na nane.",
            "pg020_n0018": "Zoezi la Tano",
            "pg020_n0020": "Swali namba moja. Soma namba zifuatazo:",
            "pg020_n0021": "Sehemu a. Elfu tisa mia tisa tisini na tisa. Elfu kumi. Elfu kumi na moja. Elfu kumi na mbili. Elfu kumi na tatu. Elfu kumi na nne.",
            "pg020_n0022": "Elfu kumi na tano. Elfu kumi na sita. Elfu kumi na saba. Elfu kumi na nane. Elfu kumi na tisa.",
            "pg020_n0023": "Sehemu b. Elfu kumi na kumi. Elfu kumi na ishirini. Elfu kumi na thelathini. Elfu kumi na arobaini. Elfu kumi na hamsini. Elfu kumi na sitini.",
            "pg020_n0024": "Elfu kumi na sabini. Elfu kumi na themanini. Elfu kumi na tisini. Elfu kumi na mia moja. Elfu kumi na mia moja na kumi.",
            "pg020_n0025": "Sehemu c. Elfu ishirini na mia mbili. Elfu ishirini na mia nne. Elfu ishirini na mia sita. Elfu ishirini na mia nane. Elfu ishirini na moja. Elfu ishirini na moja mia mbili.",
            "pg020_n0026": "Elfu ishirini na moja mia nne. Elfu ishirini na moja mia sita. Elfu ishirini na moja mia nane. Elfu ishirini na mbili. Elfu ishirini na mbili mia mbili.",
            "pg020_n0027": "Sehemu d. Elfu tisini na tisa mia tisa tisini na moja. Elfu tisini na tisa mia tisa tisini na mbili. Elfu tisini na tisa mia tisa tisini na tatu. Elfu tisini na tisa mia tisa tisini na nne. Elfu tisini na tisa mia tisa tisini na tano. Elfu tisini na tisa mia tisa tisini na sita.",
            "pg020_n0028": "Elfu tisini na tisa mia tisa tisini na saba. Elfu tisini na tisa mia tisa tisini na nane. Elfu tisini na tisa mia tisa tisini na tisa.",
        },
    },
    21: {
        "remove": {
            "pg021_n0002", "pg021_n0009", "pg021_n0011",
            "pg021_n0014", "pg021_n0016", "pg021_n0021",
        },
        "replace": {
            "pg021_n0001": "Swali namba mbili. Soma namba zifuatazo katika jedwali, kisha andika kwa maneno.",
            "pg021_n0003": "Jedwali lina safu wima mbili. Safu ya kwanza ni namba kwa tarakimu. Safu ya pili ni nafasi ya kuandika namba kwa maneno. Tunasoma mstari kwa mstari, kutoka juu kwenda chini.",
            "pg021_n0004": "Sehemu a. Namba kwa tarakimu ni 38951. Namba hii itaandikwaje kwa maneno?",
            "pg021_n0005": "Sehemu b. Namba kwa tarakimu ni 40690. Namba hii itaandikwaje kwa maneno?",
            "pg021_n0006": "Sehemu c. Namba kwa tarakimu ni 97000. Namba hii itaandikwaje kwa maneno?",
            "pg021_n0007": "Sehemu d. Namba kwa tarakimu ni 30001. Namba hii itaandikwaje kwa maneno?",
            "pg021_n0008": "Swali namba tatu. Soma namba zifuatazo, kisha andika namba hizo kwa tarakimu.",
            "pg021_n0010": "Jedwali lina safu wima mbili. Safu ya kwanza ni namba kwa maneno. Safu ya pili ni nafasi ya kuandika namba kwa tarakimu. Tunasoma mstari kwa mstari, kutoka juu kwenda chini.",
            "pg021_n0012": "Sehemu a. Namba kwa maneno ni sabini elfu mia nane na tano. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0013": "Sehemu b. Namba kwa maneno ni tisini na tisa elfu mia nane tisini na nane. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0015": "Sehemu c. Namba kwa maneno ni elfu thelathini na tatu mia sita sabini na mbili. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0017": "Sehemu d. Namba kwa maneno ni elfu ishirini na moja mia mbili na tano. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0018": "Sehemu e. Namba kwa maneno ni tisini elfu na tisa. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0019": "Sehemu f. Namba kwa maneno ni elfu hamsini. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0020": "Sehemu g. Namba kwa maneno ni sitini na tisa elfu mia moja hamsini na tano. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0022": "Sehemu h. Namba kwa maneno ni elfu tisa mia saba hamsini na tatu. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0023": "Sehemu i. Namba kwa maneno ni tisini na tisa elfu mia moja tisini na tisa. Namba hii itaandikwaje kwa tarakimu?",
            "pg021_n0024": "Sehemu j. Namba kwa maneno ni themanini elfu mia mbili na saba. Namba hii itaandikwaje kwa tarakimu?",
        },
    },
    22: {
        "remove": {
            "pg022_n0003", "pg022_n0005", "pg022_n0007",
            "pg022_n0009", "pg022_n0011", "pg022_n0012", "pg022_n0013",
        },
        "replace": {
            "pg022_n0001": "Jikumbushe.",
            "pg022_n0002": "Jambo la kwanza. Kuhesabu vitu vingi kwa urahisi zaidi, ni vizuri kufunga vitu hivyo katika mafungu, ndipo uvihesabu.",
            "pg022_n0004": "Jambo la pili. Mafungu ya vitu vya kuhesabu huweza kuwa na ukubwa tofauti.",
            "pg022_n0006": "Jambo la tatu. Thamani ya tarakimu inategemea nafasi yake katika namba.",
            "pg022_n0008": "Jambo la nne. Unapofafanua namba, zingatia nafasi ya tarakimu katika namba.",
            "pg022_n0010": "Jambo la tano. Unapoandika namba kwa kifupi, jumlisha namba zilizoandikwa kwa kirefu kupata namba moja.",
        },
    },
    23: {
        "remove": {
            "pg023_n0005", "pg023_n0006", "pg023_n0007", "pg023_n0008",
            "pg023_n0010", "pg023_n0013", "pg023_n0014", "pg023_n0016",
            "pg023_n0017", "pg023_n0018",
        },
        "replace": {
            "pg023_n0001": "Sura ya Pili.",
            "pg023_n0002": "Mpangilio wa namba nzima.",
            "pg023_n0003": "Utangulizi.",
            "pg023_n0004": "Mpangilio wa vitu ni muhimu katika maisha ya kila siku. Vitu hivyo huweza kuwa vimepangwa au vimepangiliwa kimstari, kibapa au kiukumbi, kwa asili au kwa kutengenezwa. Namba pia huweza kupangiliwa katika utaratibu maalumu. Katika sura hii, utajifunza jinsi ya kupangilia namba na vitu mbalimbali.",
            "pg023_n0009": "Mpangilio ni utaratibu maalumu wa vitu unaozingatia kanuni fulani katika maisha. Vipo vitu mbalimbali vilivyo katika mpangilio fulani.",
            "pg023_n0011": "Mfano.",
            "pg023_n0012": "Mfano wa kwanza. Mpangilio wa mistari mikubwa na midogo katika daftari la mwandiko. Daftari lililofunguliwa lina mistari ya mlalo iliyopangwa kwa kurudiarudia, mstari mkubwa ukifuatwa na mstari mdogo.",
            "pg023_n0015": "Mfano wa pili. Mpangilio wa mayai katika trei. Mayai mengi yamepangwa kwenye trei kwa mistari na safu zinazofuata utaratibu mmoja.",
        },
    },
    24: {
        "remove": {
            "pg024_n0002", "pg024_n0004", "pg024_n0005", "pg024_n0008",
            "pg024_n0011", "pg024_n0015", "pg024_n0019", "pg024_n0021",
            "pg024_n0022", "pg024_n0023",
        },
        "replace": {
            "pg024_n0001": "Mfano wa tatu. Mpangilio wa chupa za soda katika kreti. Kreti nyekundu ina chupa za soda zilizosimama na kupangwa katika mistari na safu.",
            "pg024_n0003": "Mfano wa nne. Mpangilio wa madawati, meza, na viti ndani ya darasa. Madawati na viti vimepangwa katika mistari kadhaa inayoelekea mbele ya darasa.",
            "pg024_n0006": "Kazi.",
            "pg024_n0007": "Chunguza vitu vinavyopatikana katika mazingira yako, kisha jibu maswali yafuatayo.",
            "pg024_n0009": "Swali namba moja. Taja vitu sita unavyovifahamu vilivyopo katika mpangilio.",
            "pg024_n0010": "Swali namba mbili. Orodhesha vitu vinne vinavyoonesha mpangilio uliotengenezwa na binadamu.",
            "pg024_n0012": "Swali namba tatu. Orodhesha wanyama watatu wenye rangi zenye mpangilio.",
            "pg024_n0013": "Mpangilio wa namba.",
            "pg024_n0014": "Mpangilio wa namba unaweza ukawa wa kupungua, kuongezeka, au kujirudia.",
            "pg024_n0016": "Mfano.",
            "pg024_n0017": "Chunguza mpangilio wa namba zifuatazo. Soma kutoka kushoto kwenda kulia.",
            "pg024_n0018": "Sehemu a. Elfu moja. Elfu mbili. Elfu tatu. Elfu nne. Elfu tano. Elfu sita. Elfu saba. Elfu nane. Elfu tisa. Elfu kumi. Elfu kumi na moja. Elfu kumi na mbili. Elfu kumi na tatu. Elfu kumi na nne. Elfu kumi na tano.",
            "pg024_n0020": "Mpangilio huu wa namba unaongezeka kwa elfu moja katika kila namba inayofuata.",
        },
    },
    25: {
        "remove": {
            "pg025_n0003", "pg025_n0006", "pg025_n0009", "pg025_n0011",
            "pg025_n0016", "pg025_n0021", "pg025_n0023", "pg025_n0025", "pg025_n0026",
        },
        "replace": {
            "pg025_n0001": "Sehemu b. Soma kutoka kulia kwenda kushoto. Elfu sita mia tano ishirini na tano. Elfu tano mia saba. Elfu nne mia nane sabini na tano. Elfu nne hamsini. Elfu tatu mia mbili ishirini na tano. Elfu mbili mia nne. Elfu moja mia tano sabini na tano. Mia saba hamsini.",
            "pg025_n0002": "Mpangilio huu wa namba unaongezeka kwa mia nane ishirini na tano katika kila namba inayofuata.",
            "pg025_n0004": "Sehemu c. Soma kutoka kulia kwenda kushoto. Sifuri. Hamsini. Mia moja. Mia moja hamsini. Mia mbili. Mia mbili hamsini. Mia tatu. Mia tatu hamsini.",
            "pg025_n0005": "Mpangilio huu wa namba unapungua kwa hamsini katika kila namba inayofuata.",
            "pg025_n0007": "Sehemu d. Soma kutoka kulia kwenda kushoto. Elfu tisa mia mbili arobaini na moja. Elfu tisa mia sita sitini na tisa. Elfu kumi tisini na saba. Elfu kumi mia tano ishirini na tano. Elfu kumi mia tisa hamsini na tatu. Elfu kumi na moja mia tatu themanini na moja. Elfu kumi na moja mia nane na tisa. Elfu kumi na mbili mia mbili thelathini na saba.",
            "pg025_n0008": "Mpangilio huu wa namba unapungua kwa mia nne ishirini na nane katika kila namba inayofuata.",
            "pg025_n0010": "Sehemu e. Soma kutoka kulia kwenda kushoto. Elfu sabini na nne mia nne kumi na tano. Elfu sabini na tatu mia nne kumi na nne. Elfu sabini na mbili mia nne kumi na tatu. Namba hizo tatu zinajirudia kwa mpangilio huo mara mbili zaidi tukisogea kushoto.",
            "pg025_n0012": "Mpangilio huu wa namba ni mfano wa namba zinazojirudia.",
            "pg025_n0013": "Zoezi la Kwanza.",
            "pg025_n0014": "Jibu maswali yafuatayo.",
            "pg025_n0015": "Swali namba moja. Andika mpangilio wenye idadi ya namba tano unaoongezeka kwa mia moja ishirini, kuanzia namba elfu sita mia nane ishirini.",
            "pg025_n0017": "Swali namba mbili. Andika aina ya mpangilio katika orodha za namba zifuatazo.",
            "pg025_n0018": "Sehemu a. Soma kutoka kulia kwenda kushoto. Elfu nne mia nane. Elfu nne mia saba hamsini. Elfu nne mia saba. Elfu nne mia sita hamsini. Elfu nne mia sita. Elfu nne mia tano hamsini. Elfu nne mia tano. Mpangilio huu ni wa aina gani?",
            "pg025_n0019": "Sehemu b. Soma kutoka kulia kwenda kushoto. Elfu kumi na nane ishirini na nane. Elfu ishirini na sita ishirini na nane. Elfu thelathini na nne ishirini na nane. Elfu arobaini na mbili ishirini na nane. Elfu hamsini ishirini na nane. Elfu hamsini na nane ishirini na nane. Mpangilio huu ni wa aina gani?",
            "pg025_n0020": "Sehemu c. Soma kutoka kulia kwenda kushoto. Elfu sitini na nne kumi na tatu. Elfu hamsini na nne kumi na tatu. Elfu arobaini na nne kumi na tatu. Namba hizo tatu zinajirudia kwa mpangilio huo mara mbili zaidi tukisogea kushoto. Mpangilio huu ni wa aina gani?",
            "pg025_n0022": "Swali namba tatu. Orodhesha vitu vitano vilivyopo katika mpangilio, vinavyopatikana katika mazingira yafuatayo.",
            "pg025_n0024": "Sehemu a, shuleni. Sehemu b, nyumbani. Sehemu c, sokoni.",
        },
    },
    26: {
        "remove": {
            "pg026_n0003", "pg026_n0010", "pg026_n0014", "pg026_n0027", "pg026_n0028",
            "pg026_n0007_matrix_1", "pg026_n0008_matrix_1", "pg026_n0025_matrix_1",
        },
        "replace": {
            "pg026_n0001": "Mpangilio wa namba nzima zinazopatikana kwa kujumlisha.",
            "pg026_n0002": "Namba katika mpangilio huu hupatikana kwa kufuata hatua zifuatazo.",
            "pg026_n0004": "Hatua ya kwanza. Taja namba mbili zilizotangulia.",
            "pg026_n0005": "Hatua ya pili. Tafuta tofauti ya namba mbili zilizotangulia.",
            "pg026_n0006": "Hatua ya tatu. Jumlisha tofauti ya namba hizo na namba iliyotangulia.",
            "pg026_n0007": "Mfano wa kwanza.",
            "pg026_n0008": "Jaza namba zinazokosekana katika mpangilio ufuatao.",
            "pg026_n0009": "Soma mpangilio kutoka kulia kwenda kushoto. Upande wa kulia kuna nafasi mbili zilizo wazi. Tukisogea kushoto tunakutana na: kumi na tisa, kumi na sita, kumi na tatu, kumi, saba, nne, na moja.",
            "pg026_n0011": "Hatua ya kwanza. Namba mbili zilizotangulia ni moja na nne.",
            "pg026_n0012": "Hatua ya pili. Tofauti ni nne kutoa moja, ni sawa na tatu.",
            "pg026_n0013": "Hatua ya tatu. Namba inayofuata katika mpangilio huu inapatikana kwa kujumlisha tatu kwenye namba iliyotangulia. Fuata hesabu kutoka juu kwenda chini.",
            "pg026_n0015": "Moja jumlisha tatu ni sawa na nne.",
            "pg026_n0016": "Nne jumlisha tatu ni sawa na saba.",
            "pg026_n0017": "Saba jumlisha tatu ni sawa na kumi.",
            "pg026_n0018": "Kumi jumlisha tatu ni sawa na kumi na tatu.",
            "pg026_n0019": "Kumi na tatu jumlisha tatu ni sawa na kumi na sita.",
            "pg026_n0020": "Kumi na sita jumlisha tatu ni sawa na kumi na tisa.",
            "pg026_n0021": "Kumi na tisa jumlisha tatu ni sawa na ishirini na mbili.",
            "pg026_n0022": "Ishirini na mbili jumlisha tatu ni sawa na ishirini na tano.",
            "pg026_n0023": "Kwa hiyo, mpangilio kamili ni: moja, nne, saba, kumi, kumi na tatu, kumi na sita, kumi na tisa, ishirini na mbili, na ishirini na tano. Namba zilizokosekana ni ishirini na mbili na ishirini na tano.",
            "pg026_n0024": "Mfano wa pili.",
            "pg026_n0025": "Andika namba zinazokosekana katika mpangilio ufuatao.",
            "pg026_n0026": "Soma mpangilio kutoka kulia kwenda kushoto. Upande wa kulia kuna nafasi tatu zilizo wazi. Tukisogea kushoto tunakutana na: mia tano na nne, mia nne na tatu, mia tatu na mbili, na mia mbili na moja. Endeleza mpangilio kwa kuandika namba zinazokosekana.",
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
        "remove": {"pg031_n0028", "pg031_n0029"},
        "replace": {
            "pg031_n0003": "Kwa hiyo, jibu ni: sitini na nne.",
            "pg031_n0004": "Zoezi la Nne.",
            "pg031_n0023": "Swali namba nne. Jaza namba zinazokosekana katika nafasi zilizo wazi.",
            "pg031_n0024": "Sehemu a. Tano kuzidisha dashi, sawa sawa na kumi.",
            "pg031_n0025": "Sehemu b. Dashi kuzidisha mbili, sawa sawa na mia moja.",
            "pg031_n0026": "Sehemu c. Mia tano kuzidisha mbili, sawa sawa na dashi.",
            "pg031_n0027": "Sehemu d. Dashi kuzidisha mbili, sawa sawa na elfu kumi.",
        },
    },
    33: {
        "remove": {
            "pg033_n0005", "pg033_n0006", "pg033_n0007", "pg033_n0008",
            "pg033_n0009", "pg033_n0010", "pg033_n0014", "pg033_n0025", "pg033_n0026",
        },
        "replace": {
            "pg033_n0001": "Sura ya Tatu.",
            "pg033_n0002": "Namba za Kirumi.",
            "pg033_n0003": "Utangulizi.",
            "pg033_n0004": "Namba nzima zinaundwa na tarakimu kumi ambazo ni: sifuri, moja, mbili, tatu, nne, tano, sita, saba, nane, na tisa. Namba hizi zinaitwa namba za kawaida au Kiarabu. Zipo namba za aina nyingine zinazojulikana kama namba za Kirumi. Namba za Kirumi hutumia baadhi ya herufi za alfabeti. Katika sura hii, utajifunza kutambua, kusoma, na kuandika namba za Kirumi kuanzia moja hadi hamsini.",
            "pg033_n0011": "Namba za Kirumi kuanzia moja hadi kumi.",
            "pg033_n0012": "Soma jedwali lifuatalo kwa utaratibu, mstari kwa mstari kutoka juu kwenda chini.",
            "pg033_n0013": "Jedwali lina safu wima tatu. Safu ya kwanza ni namba za kawaida. Safu ya pili ni alama za namba za Kirumi. Safu ya tatu ni namba kwa maneno.",
            "pg033_n0015": "Mstari wa kwanza. Namba ya kawaida ni moja. Alama ya Kirumi ni herufi I moja, inawakilisha moja. Namba kwa maneno ni moja.",
            "pg033_n0016": "Mstari wa pili. Namba ya kawaida ni mbili. Alama ya Kirumi ni herufi I mbili, inawakilisha mbili. Namba kwa maneno ni mbili.",
            "pg033_n0017": "Mstari wa tatu. Namba ya kawaida ni tatu. Alama ya Kirumi ni herufi I tatu, inawakilisha tatu. Namba kwa maneno ni tatu.",
            "pg033_n0018": "Mstari wa nne. Namba ya kawaida ni nne. Alama ya Kirumi ni herufi I kabla ya V, inawakilisha nne. Namba kwa maneno ni nne.",
            "pg033_n0019": "Mstari wa tano. Namba ya kawaida ni tano. Alama ya Kirumi ni herufi V, inawakilisha tano. Namba kwa maneno ni tano.",
            "pg033_n0020": "Mstari wa sita. Namba ya kawaida ni sita. Alama ya Kirumi ni V ikifuatiwa na I moja, inawakilisha sita. Namba kwa maneno ni sita.",
            "pg033_n0021": "Mstari wa saba. Namba ya kawaida ni saba. Alama ya Kirumi ni V ikifuatiwa na herufi I mbili, inawakilisha saba. Namba kwa maneno ni saba.",
            "pg033_n0022": "Mstari wa nane. Namba ya kawaida ni nane. Alama ya Kirumi ni V ikifuatiwa na herufi I tatu, inawakilisha nane. Namba kwa maneno ni nane.",
            "pg033_n0023": "Mstari wa tisa. Namba ya kawaida ni tisa. Alama ya Kirumi ni I kabla ya X, inawakilisha tisa. Namba kwa maneno ni tisa.",
            "pg033_n0024": "Mstari wa kumi. Namba ya kawaida ni kumi. Alama ya Kirumi ni herufi X, inawakilisha kumi. Namba kwa maneno ni kumi.",
        },
    },
    34: {
        "replace": {
            "pg034_n0002": "Chunguza orodha hii; 4, II, 5, IV, I, III, 2, V, na 3 kisha jibu maswali",
        },
    },
    36: {
        "remove": {
            "pg036_n0003", "pg036_n0005", "pg036_n0007", "pg036_n0009",
            "pg036_n0010", "pg036_n0012", "pg036_n0015", "pg036_n0027", "pg036_n0028",
        },
        "replace": {
            "pg036_n0001": "Namba za Kirumi kuanzia kumi na moja hadi ishirini.",
            "pg036_n0002": "Soma namba zilizomo katika jedwali lifuatalo kwa Kirumi, Kiarabu, na kwa maneno.",
            "pg036_n0004": "Jedwali lina mistari mitatu: namba za Kirumi, namba za Kiarabu, na namba kwa maneno. Tunasoma kila safu wima kwa mpangilio wa namba kumi na moja hadi ishirini.",
            "pg036_n0006": "Safu ya kumi na moja. Alama ya Kirumi ni X ikifuatiwa na I moja. Namba ya Kiarabu ni kumi na moja. Kwa maneno ni kumi na moja. Safu ya kumi na mbili. Alama ya Kirumi ni X ikifuatiwa na I mbili. Namba ya Kiarabu ni kumi na mbili. Kwa maneno ni kumi na mbili. Safu ya kumi na tatu. Alama ya Kirumi ni X ikifuatiwa na I tatu. Namba ya Kiarabu ni kumi na tatu. Kwa maneno ni kumi na tatu.",
            "pg036_n0008": "Safu ya kumi na nne. Alama ya Kirumi ni X ikifuatiwa na I kabla ya V. Namba ya Kiarabu ni kumi na nne. Kwa maneno ni kumi na nne. Safu ya kumi na tano. Alama ya Kirumi ni X ikifuatiwa na V. Namba ya Kiarabu ni kumi na tano. Kwa maneno ni kumi na tano. Safu ya kumi na sita. Alama ya Kirumi ni X ikifuatiwa na V, halafu I moja. Namba ya Kiarabu ni kumi na sita. Kwa maneno ni kumi na sita. Safu ya kumi na saba. Alama ya Kirumi ni X ikifuatiwa na V, halafu I mbili. Namba ya Kiarabu ni kumi na saba. Kwa maneno ni kumi na saba. Safu ya kumi na nane. Alama ya Kirumi ni X ikifuatiwa na V, halafu I tatu. Namba ya Kiarabu ni kumi na nane. Kwa maneno ni kumi na nane. Safu ya kumi na tisa. Alama ya Kirumi ni X ikifuatiwa na I kabla ya X. Namba ya Kiarabu ni kumi na tisa. Kwa maneno ni kumi na tisa. Safu ya ishirini. Alama ya Kirumi ni herufi X mbili. Namba ya Kiarabu ni ishirini. Kwa maneno ni ishirini.",
            "pg036_n0011": "Katika mifano ya kumi na nne na kumi na tisa, alama ya nne au ya tisa imewekwa upande wa kulia wa X. Kwa hiyo, thamani yake huongezwa kwenye kumi na kusomwa kama namba kamili.",
            "pg036_n0013": "Mfano.",
            "pg036_n0014": "Andika namba kumi na moja, kumi na mbili, kumi na nne, kumi na tano, kumi na saba, na kumi na tisa kwa namba za Kirumi.",
            "pg036_n0016": "Njia. Soma kila safu kwa kuanzia namba ya Kiarabu, kisha hatua ya kuunda alama ya Kirumi.",
            "pg036_n0017": "Safu ya kwanza, namba kumi na moja. Safu ya pili, namba kumi na mbili. Safu ya tatu, namba kumi na nne. Safu ya nne, namba kumi na tano. Safu ya tano, namba kumi na saba. Safu ya sita, namba kumi na tisa.",
            "pg036_n0018": "Kumi jumlisha moja ni kumi na moja. X ikifuatiwa na I moja huunda alama ya kumi na moja. Kumi jumlisha mbili ni kumi na mbili. X ikifuatiwa na I mbili huunda alama ya kumi na mbili. Kumi jumlisha nne ni kumi na nne. X ikifuatiwa na I kabla ya V huunda alama ya kumi na nne. Kumi jumlisha tano ni kumi na tano. X ikifuatiwa na V huunda alama ya kumi na tano. Kumi jumlisha saba ni kumi na saba. X ikifuatiwa na V na I mbili huunda alama ya kumi na saba. Kumi jumlisha tisa ni kumi na tisa. X ikifuatiwa na I kabla ya X huunda alama ya kumi na tisa.",
            "pg036_n0019": "Zoezi la Pili.",
            "pg036_n0020": "Jibu maswali yafuatayo.",
            "pg036_n0021": "Swali namba moja. Namba ipi ina thamani kubwa zaidi katika orodha ifuatayo?",
            "pg036_n0022": "Alama ya kwanza, X ikifuatiwa na I moja. Ya pili, X ikifuatiwa na I mbili. Ya tatu, X ikifuatiwa na I tatu. Ya nne, X ikifuatiwa na V. Ya tano, X ikifuatiwa na V na I moja. Ya sita, X ikifuatiwa na V na I mbili. Ya saba, X ikifuatiwa na V na I tatu. Ya nane, X ikifuatiwa na I kabla ya V. Ya tisa, X ikifuatiwa na I kabla ya X. Bainisha alama yenye thamani kubwa zaidi.",
            "pg036_n0023": "Swali namba mbili. Andika kwa maneno namba za Kirumi zifuatazo.",
            "pg036_n0024": "Sehemu a. X ikifuatiwa na I kabla ya V. Sehemu d. X ikifuatiwa na I moja.",
            "pg036_n0025": "Sehemu b. X ikifuatiwa na V na I moja. Sehemu e. X ikifuatiwa na V.",
            "pg036_n0026": "Sehemu c. Herufi X mbili. Sehemu f. X ikifuatiwa na I kabla ya X.",
        },
    },
    37: {
        "remove": {
            "pg037_n0002", "pg037_n0004", "pg037_n0005", "pg037_n0006",
            "pg037_n0008", "pg037_n0010", "pg037_n0012", "pg037_n0028", "pg037_n0029",
        },
        "replace": {
            "pg037_n0001": "Swali namba tatu. Andika namba za Kiarabu zifuatazo kwa namba za Kirumi.",
            "pg037_n0003": "Jedwali lina mistari miwili. Mstari wa juu una namba za Kiarabu. Mstari wa chini una nafasi za kuandika namba za Kirumi. Soma namba za Kiarabu kutoka kulia kwenda kushoto: kumi na tano, kumi na moja, kumi na nane, kumi na mbili, kumi na nne, ishirini, kumi na sita, kumi na tatu, kumi na saba, na kumi na tisa. Andika alama ya Kirumi inayolingana chini ya kila namba.",
            "pg037_n0007": "Swali namba nne. Andika namba za Kirumi zifuatazo kwa namba za Kiarabu.",
            "pg037_n0009": "Jedwali lina mistari miwili. Mstari wa juu una alama za Kirumi. Mstari wa chini una nafasi za kuandika namba za Kiarabu. Soma kutoka kulia kwenda kushoto. Alama ya kwanza ni X ikifuatiwa na I mbili. Ya pili ni X ikifuatiwa na I kabla ya V. Ya tatu ni X ikifuatiwa na V na I mbili. Ya nne ni X ikifuatiwa na V. Ya tano ni X ikifuatiwa na V na I tatu. Ya sita ni X ikifuatiwa na I moja. Andika namba ya Kiarabu inayolingana chini ya kila alama.",
            "pg037_n0011": "Swali namba tano. Andika namba zinazokosekana katika kila mpangilio ufuatao.",
            "pg037_n0013": "Sehemu a. Soma kutoka kulia kwenda kushoto. Herufi X mbili, nafasi ya kwanza iliyo wazi, X ikifuatiwa na V na I moja, X ikifuatiwa na I kabla ya V, nafasi ya pili iliyo wazi, kisha herufi X moja. Jaza nafasi mbili bila kubadilisha mpangilio.",
            "pg037_n0014": "Sehemu b. Soma kutoka kulia kwenda kushoto. Herufi X moja, nafasi ya kwanza iliyo wazi, X ikifuatiwa na I mbili, nafasi ya pili iliyo wazi, X ikifuatiwa na I kabla ya V, kisha nafasi ya tatu iliyo wazi. Jaza nafasi tatu bila kubadilisha mpangilio.",
            "pg037_n0015": "Namba za Kirumi kuanzia ishirini na moja hadi thelathini na tatu.",
            "pg037_n0016": "Soma jedwali lifuatalo mstari kwa mstari kutoka juu kwenda chini. Sehemu iliyopo kwenye ukurasa huu inaanzia ishirini na moja hadi thelathini.",
            "pg037_n0017": "Jedwali lina safu wima mbili. Safu ya kwanza ina alama za Kirumi. Safu ya pili ina namba za kawaida.",
            "pg037_n0018": "Mstari wa kwanza. Alama ya Kirumi ni herufi X mbili zikifuatiwa na I moja. Inawakilisha namba ishirini na moja.",
            "pg037_n0019": "Mstari wa pili. Alama ya Kirumi ni herufi X mbili zikifuatiwa na I mbili. Inawakilisha namba ishirini na mbili.",
            "pg037_n0020": "Mstari wa tatu. Alama ya Kirumi ni herufi X mbili zikifuatiwa na I tatu. Inawakilisha namba ishirini na tatu.",
            "pg037_n0021": "Mstari wa nne. Alama ya Kirumi ni herufi X mbili zikifuatiwa na I kabla ya V. Inawakilisha namba ishirini na nne.",
            "pg037_n0022": "Mstari wa tano. Alama ya Kirumi ni herufi X mbili zikifuatiwa na V. Inawakilisha namba ishirini na tano.",
            "pg037_n0023": "Mstari wa sita. Alama ya Kirumi ni herufi X mbili zikifuatiwa na V na I moja. Inawakilisha namba ishirini na sita.",
            "pg037_n0024": "Mstari wa saba. Alama ya Kirumi ni herufi X mbili zikifuatiwa na V na I mbili. Inawakilisha namba ishirini na saba.",
            "pg037_n0025": "Mstari wa nane. Alama ya Kirumi ni herufi X mbili zikifuatiwa na V na I tatu. Inawakilisha namba ishirini na nane.",
            "pg037_n0026": "Mstari wa tisa. Alama ya Kirumi ni herufi X mbili zikifuatiwa na I kabla ya X. Inawakilisha namba ishirini na tisa.",
            "pg037_n0027": "Mstari wa kumi. Alama ya Kirumi ni herufi X tatu. Inawakilisha namba thelathini.",
        },
    },
    38: {
        "remove": {"pg038_n0020", "pg038_n0025", "pg038_n0026"},
        "replace": {
            "pg038_n0001": "Mwendelezo wa jedwali. Mstari wa kumi na moja. Alama ya Kirumi ni herufi X tatu zikifuatiwa na I moja. Inawakilisha namba thelathini na moja.",
            "pg038_n0002": "Mstari wa kumi na mbili. Alama ya Kirumi ni herufi X tatu zikifuatiwa na I mbili. Inawakilisha namba thelathini na mbili.",
            "pg038_n0003": "Mstari wa kumi na tatu. Alama ya Kirumi ni herufi X tatu zikifuatiwa na I tatu. Inawakilisha namba thelathini na tatu.",
            "pg038_n0004": "Mfano.",
            "pg038_n0005": "Andika namba zifuatazo kwa Kirumi.",
            "pg038_n0006": "Sehemu a, ishirini na nne. Sehemu b, thelathini. Sehemu c, ishirini na saba.",
            "pg038_n0007": "Jibu.",
            "pg038_n0008": "Sehemu a. Ishirini na nne ni kumi jumlisha kumi, jumlisha nne. Nne ni tano kutoa moja. Kwa hiyo, ishirini na nne kwa Kirumi ni herufi X mbili zikifuatiwa na I kabla ya V.",
            "pg038_n0009": "Sehemu b. Thelathini ni kumi jumlisha kumi, jumlisha kumi. Kwa hiyo, thelathini kwa Kirumi ni herufi X tatu.",
            "pg038_n0010": "Sehemu c. Ishirini na saba ni kumi jumlisha kumi, jumlisha tano, jumlisha mbili. Kwa hiyo, ishirini na saba kwa Kirumi ni herufi X mbili zikifuatiwa na V na I mbili.",
            "pg038_n0011": "Zoezi la Tatu.",
            "pg038_n0012": "Jibu maswali yafuatayo.",
            "pg038_n0013": "Swali namba moja. Andika namba zifuatazo kwa Kirumi.",
            "pg038_n0014": "Sehemu a, ishirini na tisa. Sehemu c, thelathini na mbili.",
            "pg038_n0015": "Sehemu b, ishirini na sita. Sehemu d, ishirini na tatu.",
            "pg038_n0016": "Swali namba mbili. Andika namba zifuatazo kwa Kiarabu.",
            "pg038_n0017": "Sehemu a. Herufi X mbili zikifuatiwa na I mbili. Sehemu c. Herufi X mbili zikifuatiwa na V na I tatu.",
            "pg038_n0018": "Sehemu b. Herufi X tatu zikifuatiwa na I moja. Sehemu d. Herufi X mbili zikifuatiwa na V.",
            "pg038_n0019": "Swali namba tatu. Andika namba za Kirumi zinazokosekana katika mipangilio ifuatayo. Soma kila mpangilio kutoka kulia kwenda kushoto.",
            "pg038_n0021": "Sehemu a. Herufi X mbili zikifuatiwa na V na I moja; dashi; dashi; herufi X mbili zikifuatiwa na I tatu; dashi; kisha herufi X mbili zikifuatiwa na I moja.",
            "pg038_n0022": "Sehemu b. Dashi; dashi; dashi; herufi X mbili zikifuatiwa na I kabla ya X; dashi; dashi; herufi X mbili zikifuatiwa na V na I moja; dashi; kisha herufi X mbili zikifuatiwa na I kabla ya V.",
            "pg038_n0023": "Sehemu c. Herufi X mbili zikifuatiwa na V na I moja; dashi; herufi X mbili zikifuatiwa na V na I tatu; dashi; herufi X tatu; dashi; kisha herufi X tatu zikifuatiwa na I mbili.",
            "pg038_n0024": "Sehemu d. Dashi; herufi X mbili zikifuatiwa na I mbili; herufi X mbili zikifuatiwa na I tatu; dashi; herufi X mbili zikifuatiwa na V; dashi; kisha dashi.",
        },
    },
    40: {
        "remove": {"pg040_n0027", "pg040_n0028"},
        "replace": {
            "pg040_n0001": "Mfano wa Pili.",
            "pg040_n0002": "Andika arobaini kwa namba za Kirumi.",
            "pg040_n0003": "Jibu.",
            "pg040_n0004": "Arobaini sawa sawa na hamsini kutoa kumi.",
            "pg040_n0005": "Kwa hiyo, arobaini kwa namba za Kirumi ni alama X ikifuatiwa na L.",
        },
    },
    41: {
        "replace": {
            "pg041_n0001": "Swali namba nane. Jaza nafasi zilizoachwa wazi katika jedwali lifuatalo.",
            "pg041_n0002": "Jedwali lina mistari miwili na safu nne za kujaza. Mstari wa juu una namba za Kiarabu. Mstari wa chini una namba za Kirumi. Tunasoma kila safu kwa mpangilio, kutoka chumba cha juu kwenda chumba cha chini.",
            "pg041_n0003": "Safu ya kwanza. Chumba cha namba za Kiarabu kiko wazi. Namba ya Kiarabu ni ngapi? Chumba cha namba za Kirumi kina exi, exi, exi, vii, aii. Safu ya pili. Chumba cha namba za Kiarabu kina thelathini na saba. Chumba cha namba za Kirumi kiko wazi. Namba ya Kirumi ni ngapi? Safu ya tatu. Chumba cha namba za Kiarabu kiko wazi. Namba ya Kiarabu ni ngapi? Chumba cha namba za Kirumi kina exi, eli. Safu ya nne. Chumba cha namba za Kiarabu kina arobaini na tisa. Chumba cha namba za Kirumi kiko wazi. Namba ya Kirumi ni ngapi?",
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
    55: {
        "remove": {"pg055_n0002", "pg055_n0004", "pg055_n0006", "pg055_n0008", "pg055_n0010"},
        "replace": {
            "pg055_n0001": "Swali namba 11. Mpangilio wa wima. Namba ya juu ni 84446. Namba ya chini ni 35260. Pangilia mamoja upande wa kulia, kisha toa namba ya chini kutoka namba ya juu. Jibu ni ngapi? Swali namba 12. Mpangilio wa wima. Namba ya juu ni 43346. Namba ya chini ni 32116. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 13. Mpangilio wa wima. Namba ya juu ni 87162. Namba ya chini ni 57051. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg055_n0003": "Swali namba 14. Mpangilio wa wima. Namba ya juu ni 58796. Namba ya chini ni 38560. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 15. Mpangilio wa wima. Namba ya juu ni 95457. Namba ya chini ni 3353. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 16. Mpangilio wa wima. Namba ya juu ni 67085. Namba ya chini ni 52054. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg055_n0005": "Swali namba 17. Mpangilio wa wima. Namba ya juu ni 58766. Namba ya chini ni 35240. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 18. Mpangilio wa wima. Namba ya juu ni 95457. Namba ya chini ni 3313. Namba ya chini ina tarakimu nne, hivyo nafasi ya makumi elfu iko wazi. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 19. Mpangilio wa wima. Namba ya juu ni 62845. Namba ya chini ni 51024. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg055_n0007": "Swali namba 20. Mpangilio wa wima. Namba ya juu ni 34276. Namba ya chini ni 32030. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 21. Mpangilio wa wima. Namba ya juu ni 54679. Namba ya chini ni 43655. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba 22. Mpangilio wa wima. Namba ya juu ni 20645. Namba ya chini ni 10035. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg055_n0009": "Swali namba 23. Mpangilio wa wima. Namba ya juu ni 78257. Namba ya chini ni 26123. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg055_n0012": "Mfano wa Kwanza",
            "pg055_n0014": "Namba ya juu ni 6854.",
            "pg055_n0015": "Namba ya chini ni 3887. Alama ni kutoa.",
        },
    },
    56: {
        "remove": {
            "pg056_n0003", "pg056_n0004", "pg056_n0005", "pg056_n0006", "pg056_n0007", "pg056_n0008", "pg056_n0009", "pg056_n0010",
            "pg056_n0012", "pg056_n0013", "pg056_n0014", "pg056_n0015", "pg056_n0016", "pg056_n0017", "pg056_n0018", "pg056_n0019",
            "pg056_n0021", "pg056_n0022", "pg056_n0023", "pg056_n0024", "pg056_n0025", "pg056_n0026", "pg056_n0027", "pg056_n0028",
            "pg056_n0030", "pg056_n0031", "pg056_n0032", "pg056_n0033", "pg056_n0036", "pg056_n0037",
        },
        "replace": {
            "pg056_n0001": "Hatua na njia ya kutoa kwa mpangilio wa wima.",
            "pg056_n0002": "Hatua ya Kwanza, upande wa kushoto. Toa mamoja. Nne kutoa saba haitoshelezi. Chukua fungu moja la makumi kutoka kwenye makumi matano. Makumi matano yanabaki makumi arobaini. Badili fungu hilo kuwa mamoja kumi, kisha jumlisha na mamoja manne. Kumi kuongeza nne ni kumi na nne. Kumi na nne kutoa saba ni saba. Andika saba katika nafasi ya mamoja. Upande wa kulia, njia inaonesha elfu sita mia nane hamsini na nne kutoa elfu tatu mia nane themanini na saba. Baada ya hatua hii, tarakimu saba imeandikwa katika nafasi ya mamoja.",
            "pg056_n0011": "Hatua ya Pili, upande wa kushoto. Toa makumi. Makumi manne kutoa makumi manane haitoshelezi. Chukua fungu moja la mamia kutoka kwenye mamia manane. Mamia manane yanabaki mamia saba. Badili fungu hilo kuwa makumi kumi, kisha jumlisha na makumi manne. Kumi kuongeza nne ni kumi na nne. Kumi na nne kutoa nane ni sita. Andika sita katika nafasi ya makumi. Upande wa kulia, njia inaonesha tarakimu sita imeongezwa kushoto kwa saba; sehemu ya jibu iliyopatikana sasa ni sitini na saba.",
            "pg056_n0020": "Hatua ya Tatu, upande wa kushoto. Toa mamia. Mamia saba kutoa mamia manane haitoshelezi. Chukua fungu moja la maelfu kutoka kwenye maelfu sita. Maelfu sita yanabaki maelfu matano. Badili fungu hilo kuwa mamia kumi, kisha jumlisha na mamia saba. Kumi kuongeza saba ni kumi na saba. Kumi na saba kutoa nane ni tisa. Andika tisa katika nafasi ya mamia. Upande wa kulia, njia inaonesha tarakimu tisa imeongezwa kushoto kwa sitini na saba; sehemu ya jibu iliyopatikana sasa ni mia tisa sitini na saba.",
            "pg056_n0029": "Hatua ya Nne, upande wa kushoto. Toa maelfu. Tano kutoa tatu ni mbili. Andika mbili katika nafasi ya maelfu. Upande wa kulia, njia inaonesha jibu kamili: elfu mbili mia tisa sitini na saba. Kwa hiyo, elfu sita mia nane hamsini na nne kutoa elfu tatu mia nane themanini na saba, sawa sawa na elfu mbili mia tisa sitini na saba.",
            "pg056_n0034": "Mfano wa Pili",
            "pg056_n0035": "Tumia mpangilio wa wima kutafuta jibu la swali lifuatalo. Namba ya juu ni elfu hamsini na saba mia sita tisini na tatu. Namba ya chini ni elfu thelathini na nne mia tano sitini na nne. Pangilia mamoja upande wa kulia, kisha toa hatua kwa hatua kuanzia mamoja kuelekea makumi elfu. Jibu ni ngapi?",
        },
    },
    59: {
        "remove": {"pg059_n0002", "pg059_n0004", "pg059_n0006"},
        "replace": {
            "pg059_n0001": "Swali namba kumi na nne. Mpangilio wa wima. Namba ya juu ni elfu hamsini na themanini na saba. Alama ni kutoa. Namba ya chini ni elfu thelathini na tano mia mbili tisini. Pangilia mamoja upande wa kulia, kisha toa namba ya chini kutoka namba ya juu. Jibu ni ngapi? Swali namba kumi na tano. Mpangilio wa wima. Namba ya juu ni elfu sabini. Alama ni kutoa. Namba ya chini ni elfu mbili mia saba sitini na nne. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba kumi na sita. Mpangilio wa wima. Namba ya juu ni elfu thelathini na moja mia moja arobaini na nne. Alama ni kutoa. Namba ya chini ni elfu ishirini na mbili na hamsini na tisa. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg059_n0003": "Swali namba kumi na saba. Mpangilio wa wima. Namba ya juu ni elfu sabini na sita mia nne thelathini na mbili. Alama ni kutoa. Namba ya chini ni elfu thelathini na saba mia tisa thelathini na tano. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba kumi na nane. Mpangilio wa wima. Namba ya juu ni elfu tisini na mbili mia saba arobaini na tatu. Alama ni kutoa. Namba ya chini ni elfu sitini na tano mia mbili sitini na tano. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi? Swali namba kumi na tisa. Mpangilio wa wima. Namba ya juu ni elfu themanini na saba mia tano thelathini na sita. Alama ni kutoa. Namba ya chini ni elfu sitini na sita mia saba arobaini na tatu. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
            "pg059_n0005": "Swali namba ishirini. Mpangilio wa wima. Namba ya juu ni elfu tisini na nne na nane. Alama ni kutoa. Namba ya chini ni elfu sabini na saba mia tatu ishirini. Pangilia mamoja upande wa kulia, kisha toa. Jibu ni ngapi?",
        },
    },
    62: {
        "remove": {"pg062_n0021", "pg062_n0022"},
        "replace": {
            "pg062_n0015": "Mfano wa Kwanza",
            "pg062_n0016": "Mbili kuzidisha moja, sawa sawa na ngapi?",
            "pg062_n0018": "Tendo hili husomwa: mbili kuzidisha moja.",
            "pg062_n0019": "Sehemu a. Namba ya kwanza ni mbili. Namba hii inawakilisha idadi ya vitu vilivyomo katika kundi.",
            "pg062_n0020": "Sehemu b. Namba inayofuata baada ya alama ya kuzidisha ni moja. Namba hii inawakilisha idadi ya makundi.",
            "pg062_n0023": "Maelezo ya picha kwenye njia. Kuna kundi moja lenye vikombe viwili. Baada ya alama ya sawa sawa, matokeo yana vikombe viwili. Hivyo, vikombe viwili katika kundi moja vinafanya jumla ya vikombe viwili.",
            "pg062_n0024": "Hivyo, mbili kuzidisha moja inawakilisha vitu viwili katika kundi moja.",
            "pg062_n0025": "Kwa hiyo, mbili kuzidisha moja, sawa sawa na mbili.",
        },
    },
    63: {
        "remove": {"pg063_n0007", "pg063_n0015", "pg063_n0023"},
        "replace": {
            "pg063_n0001": "Mfano wa Pili",
            "pg063_n0002": "Tendo la kuzidisha ni: mbili kuzidisha mbili, sawa sawa na nne.",
            "pg063_n0003": "Njia kwa kutumia makundi ya vitu katika mchoro.",
            "pg063_n0004": "Soma mchoro kutoka kushoto kwenda kulia.",
            "pg063_n0005": "Maelezo ya picha kwenye njia. Vijiti viwili vimejumlishwa na vijiti viwili; jumla ni vijiti vinne. Kundi la kwanza lina vijiti viwili. Alama ya kujumlisha. Kundi la pili lina vijiti viwili. Alama ya sawa sawa. Matokeo yana vijiti vinne. Namba ya kwanza, mbili, ni idadi ya vijiti katika kila kundi. Namba ya pili, mbili, ni idadi ya makundi.",
            "pg063_n0006": "Hivyo, mbili kuzidisha mbili inawakilisha vijiti viwili viwili katika makundi mawili.",
            "pg063_n0008": "Kwa hiyo, mbili kuzidisha mbili, sawa sawa na nne.",
            "pg063_n0009": "Mfano wa Tatu",
            "pg063_n0010": "Tendo la kuzidisha ni: tatu kuzidisha mbili, sawa sawa na sita.",
            "pg063_n0011": "Njia kwa kutumia makundi ya vitu katika mchoro.",
            "pg063_n0012": "Soma mchoro kutoka kushoto kwenda kulia.",
            "pg063_n0013": "Maelezo ya picha kwenye njia. Mipira mitatu imejumlishwa na mipira mitatu; jumla ni mipira sita. Kundi la kwanza lina mipira mitatu. Alama ya kujumlisha. Kundi la pili lina mipira mitatu. Alama ya sawa sawa. Matokeo yana mipira sita. Namba ya kwanza, tatu, ni idadi ya mipira katika kila kundi. Namba ya pili, mbili, ni idadi ya makundi.",
            "pg063_n0014": "Hivyo, tatu kuzidisha mbili inawakilisha mipira mitatu mitatu katika makundi mawili.",
            "pg063_n0016": "Kwa hiyo, tatu kuzidisha mbili, sawa sawa na sita.",
            "pg063_n0017": "Mfano wa Nne",
            "pg063_n0018": "Tendo la kuzidisha ni: nne kuzidisha tatu, sawa sawa na kumi na mbili.",
            "pg063_n0019": "Njia kwa kutumia makundi ya vitu katika mchoro.",
            "pg063_n0020": "Soma mchoro kutoka kushoto kwenda kulia.",
            "pg063_n0021": "Maelezo ya picha kwenye njia. Visoda vinne vimejumlishwa na visoda vinne, kisha vimejumlishwa na visoda vinne; jumla ni visoda kumi na mbili. Kundi la kwanza lina visoda vinne. Alama ya kujumlisha. Kundi la pili lina visoda vinne. Alama ya kujumlisha. Kundi la tatu lina visoda vinne. Alama ya sawa sawa. Matokeo yana visoda kumi na mbili. Namba ya kwanza, nne, ni idadi ya visoda katika kila kundi. Namba ya pili, tatu, ni idadi ya makundi.",
            "pg063_n0022": "Hivyo, nne kuzidisha tatu inawakilisha visoda vinne vinne katika makundi matatu.",
            "pg063_n0024": "Kwa hiyo, nne kuzidisha tatu, sawa sawa na kumi na mbili.",
        },
    },
    64: {
        "remove": {"pg064_n0005", "pg064_n0006", "pg064_n0008", "pg064_n0009", "pg064_n0011", "pg064_n0012"},
        "replace": {
            "pg064_n0003": "Chati ina safu mbili: tendo la kuzidisha, na mchoro wa vitu pamoja na nafasi ya kuandika jawabu. Tunasoma kila mstari hadi ukamilike kabla ya kuhamia mstari unaofuata.",
            "pg064_n0004": "Mstari wa kwanza. Swali namba moja. Tendo ni nne kuzidisha mbili, sawa sawa na ngapi? Maelezo ya picha kwenye njia. Soma mchoro kutoka kushoto kwenda kulia. Magari manne yamejumlishwa na magari manne. Alama ya sawa sawa inafuatiwa na nafasi ya jawabu iliyo wazi. Namba ya kwanza, nne, ni idadi ya magari katika kila kundi. Namba ya pili, mbili, ni idadi ya makundi. Jumla ya magari ni mangapi?",
            "pg064_n0007": "Mstari wa pili. Swali namba mbili. Tendo ni sita kuzidisha tatu, sawa sawa na ngapi? Maelezo ya picha kwenye njia. Soma mchoro kutoka kushoto kwenda kulia. Penseli sita zimejumlishwa na penseli sita, kisha zimejumlishwa na penseli sita. Alama ya sawa sawa inafuatiwa na nafasi ya jawabu iliyo wazi. Namba ya kwanza, sita, ni idadi ya penseli katika kila kundi. Namba ya pili, tatu, ni idadi ya makundi. Jumla ya penseli ni ngapi?",
            "pg064_n0010": "Mstari wa tatu. Swali namba tatu. Tendo la kuzidisha lina nafasi mbili zilizo wazi. Maelezo ya picha kwenye njia. Soma mchoro kutoka kushoto kwenda kulia. Kengele tatu zimejumlishwa na kengele tatu, kisha zimejumlishwa na kengele tatu. Alama ya sawa sawa inafuatiwa na nafasi ya jawabu iliyo wazi. Namba ya kwanza, inayowakilisha kengele katika kila kundi, ni ngapi? Namba ya pili, inayowakilisha idadi ya makundi, ni ngapi? Jumla ya kengele ni ngapi?",
        },
    },
    66: {
        "replace": {
            "pg066_n0001": "Mfano wa Kwanza",
            "pg066_n0003": "Hatua za shughuli.",
            "pg066_n0004": "Hatua ya kwanza. Andaa makasha matatu na chupa tatu.",
            "pg066_n0005": "Hatua ya pili. Panga makasha matatu pamoja, kutoka kushoto kwenda kulia.",
            "pg066_n0006": "Hatua ya tatu. Weka chupa moja katika kila kasha.",
            "pg066_n0007": "Hatua ya nne. Hesabu idadi ya chupa zilizomo kwenye makasha.",
            "pg066_n0008": "Maelezo ya picha ya kwanza. Mchoro una makasha matatu yaliyopangwa kwa mstari. Kila kasha lina chupa moja. Chupa moja imejumlishwa na chupa moja, kisha imejumlishwa na chupa moja; jumla ni chupa tatu. Hivyo, kuna makundi matatu, na kila kundi lina chupa moja.",
            "pg066_n0009": "Idadi ya makasha ni tatu. Idadi ya chupa katika kila kasha ni moja.",
            "pg066_n0010": "Kwa hiyo, tatu kuzidisha moja, sawa sawa na tatu.",
            "pg066_n0011": "Hatua ya tano. Toa chupa moja kutoka katika kila kasha. Kila kasha linabaki bila chupa.",
            "pg066_n0012": "Maelezo ya picha ya pili. Mchoro una makasha matatu yaliyopangwa kwa mstari. Makasha yote hayana chupa; kila kasha lina chupa sifuri. Sifuri imejumlishwa na sifuri, kisha imejumlishwa na sifuri; jumla ni sifuri.",
            "pg066_n0013": "Idadi ya makasha ni tatu. Idadi ya chupa katika kila kasha ni sifuri.",
            "pg066_n0014": "Kwa hiyo, tatu kuzidisha sifuri, sawa sawa na sifuri.",
            "pg066_n0015": "Hitimisho. Namba yoyote ikizidishwa kwa sifuri, jibu lake ni sifuri.",
            "pg066_n0016": "Vilevile, sifuri ikizidishwa kwa namba yoyote, jibu lake ni sifuri.",
            "pg066_n0017": "Mwisho wa mfano.",
        },
    },
    67: {
        "replace": {
            "pg067_n0001": "Mfano wa Pili",
            "pg067_n0002": "Sifuri kuzidisha nne, sawa sawa na ngapi?",
            "pg067_n0003": "Njia kwa kutumia picha na kujumlisha sifuri kwa kurudia.",
            "pg067_n0004": "Maelezo ya picha kwenye njia. Mchoro unasomwa kutoka kushoto kwenda kulia. Kuna makundi manne yanayooneshwa kwa visanduku. Kila kisanduku hakina kitu; kwa hiyo kila kundi lina vitu sifuri. Kundi la kwanza lenye sifuri, jumlisha kundi la pili lenye sifuri, jumlisha kundi la tatu lenye sifuri, jumlisha kundi la nne lenye sifuri, sawa sawa na sifuri. Kisanduku cha matokeo pia hakina kitu.",
            "pg067_n0005": "Kwa tarakimu: sifuri jumlisha sifuri, jumlisha sifuri, jumlisha sifuri, sawa sawa na sifuri.",
            "pg067_n0006": "Namba ya kwanza, sifuri, ni idadi ya vitu katika kila kundi. Namba ya pili, nne, ni idadi ya makundi.",
            "pg067_n0007": "Makundi yote manne hayana kitu ndani.",
            "pg067_n0008": "Kwa hiyo, kujumlisha sifuri kwa kurudia katika makundi manne kunatoa sifuri.",
            "pg067_n0009": "Kwa hiyo, sifuri kuzidisha nne, sawa sawa na sifuri.",
            "pg067_n0010": "Mfano wa Tatu",
            "pg067_n0011": "Sifuri kuzidisha tano, sawa sawa na ngapi?",
            "pg067_n0012": "Jibu.",
            "pg067_n0013": "Sifuri kuzidisha tano, sawa sawa na sifuri.",
        },
    },
    68: {
        "rate": 0.85,
        "remove": {"pg068_n0003", "pg068_n0006", "pg068_n0010", "pg068_n0011", "pg068_n0015", "pg068_n0021"},
        "replace": {
            "pg068_n0001": "Mfano wa Kwanza",
            "pg068_n0002": "Mpangilio wa wima. Namba ya juu ni arobaini na nane. Namba ya chini ni mbili, ikiwa na alama ya kuzidisha. Tarakimu mbili imepangwa chini ya tarakimu nane katika nafasi ya mamoja. Tendo ni arobaini na nane kuzidisha mbili.",
            "pg068_n0004": "Hatua. Hesabu inaanzia upande wa kulia, kwenye mamoja, kisha inaelekea kushoto kwenye makumi.",
            "pg068_n0005": "Hatua ya kwanza. Zidisha mamoja: nane kuzidisha mbili, sawa sawa na kumi na sita. Kumi na sita ni makumi moja na mamoja sita.",
            "pg068_n0007": "Hatua ya pili. Andika sita katika nafasi ya mamoja. Beba moja kwenda nafasi ya makumi.",
            "pg068_n0008": "Hatua ya tatu. Zidisha makumi: nne kuzidisha mbili, sawa sawa na nane.",
            "pg068_n0009": "Hatua ya nne. Jumlisha nane na moja iliyobebwa kutoka hatua ya pili. Nane jumlisha moja, sawa sawa na tisa. Andika tisa katika nafasi ya makumi.",
            "pg068_n0012": "Kwa hiyo, arobaini na nane kuzidisha mbili, sawa sawa na tisini na sita.",
            "pg068_n0013": "Mfano wa Pili",
            "pg068_n0014": "Mpangilio wa wima. Namba ya juu ni thelathini na moja. Namba ya chini ni saba, ikiwa na alama ya kuzidisha. Tarakimu saba imepangwa chini ya tarakimu moja katika nafasi ya mamoja. Tendo ni thelathini na moja kuzidisha saba.",
            "pg068_n0016": "Hatua. Hesabu inaanzia upande wa kulia, kwenye mamoja, kisha inaelekea kushoto kwenye makumi.",
            "pg068_n0017": "Hatua ya kwanza. Zidisha mamoja: moja kuzidisha saba, sawa sawa na saba.",
            "pg068_n0018": "Hatua ya pili. Andika saba katika nafasi ya mamoja.",
            "pg068_n0019": "Hatua ya tatu. Zidisha makumi: tatu kuzidisha saba, sawa sawa na ishirini na moja. Hii ni mamia mawili na makumi moja.",
            "pg068_n0020": "Hatua ya nne. Andika moja katika nafasi ya makumi, kisha andika mbili katika nafasi ya mamia.",
            "pg068_n0022": "Kwa hiyo, thelathini na moja kuzidisha saba, sawa sawa na mia mbili kumi na saba.",
        },
    },
    70: {
        "rate": 0.85,
        "remove": {"pg070_n0002", "pg070_n0004", "pg070_n0011", "pg070_n0016", "pg070_n0017"},
        "replace": {
            "pg070_n0001": "Swali namba kumi na saba. Mpangilio wa wima. Namba ya juu ni ishirini na nne. Namba ya chini ni mbili, ikiwa na alama ya kuzidisha. Ishirini na nne kuzidisha mbili, sawa sawa na ngapi? Swali namba kumi na nane. Mpangilio wa wima. Namba ya juu ni themanini na nne. Namba ya chini ni sita, ikiwa na alama ya kuzidisha. Themanini na nne kuzidisha sita, sawa sawa na ngapi? Swali namba kumi na tisa. Mpangilio wa wima. Namba ya juu ni arobaini na tatu. Namba ya chini ni saba, ikiwa na alama ya kuzidisha. Arobaini na tatu kuzidisha saba, sawa sawa na ngapi?",
            "pg070_n0003": "Swali namba ishirini. Mpangilio wa wima. Namba ya juu ni tisini. Namba ya chini ni tisa, ikiwa na alama ya kuzidisha. Tisini kuzidisha tisa, sawa sawa na ngapi?",
            "pg070_n0007": "Mfano wa Kwanza",
            "pg070_n0008": "Ishirini na tatu kuzidisha ishirini na moja, sawa sawa na ngapi?",
            "pg070_n0009": "Hatua. Hesabu inaanzia tarakimu ya mamoja ya kizidisho, kisha tarakimu ya makumi.",
            "pg070_n0010": "Hatua ya kwanza. Zidisha mamoja tatu kwa mamoja moja. Tatu kuzidisha moja, sawa sawa na tatu. Andika tatu katika nafasi ya mamoja.",
            "pg070_n0012": "Mwisho wa hatua ya kwanza, jibu la sehemu ya kwanza ni ishirini na tatu.",
            "pg070_n0013": "Hatua ya pili. Zidisha tarakimu mbili iliyo katika nafasi ya makumi kwa tarakimu moja iliyo katika nafasi ya mamoja. Mbili kuzidisha moja, sawa sawa na mbili. Andika mbili katika nafasi ya makumi. Jibu la mstari wa kwanza linakuwa ishirini na tatu.",
            "pg070_n0014": "Sasa tumemaliza kuzidisha ishirini na tatu kwa tarakimu moja ya mamoja.",
            "pg070_n0015": "Hatua ya tatu. Hamia tarakimu mbili iliyo katika nafasi ya makumi ya kizidisho. Zidisha tarakimu tatu ya mamoja kwa tarakimu mbili ya makumi. Tatu kuzidisha mbili, sawa sawa na sita. Kwa sababu tarakimu mbili ipo katika nafasi ya makumi, andika sifuri katika nafasi ya mamoja na sita katika nafasi ya makumi.",
            "pg070_n0018": "Hatua ya nne. Zidisha tarakimu mbili ya makumi katika namba ishirini na tatu kwa tarakimu mbili ya makumi katika namba ishirini na moja. Mbili kuzidisha mbili, sawa sawa na nne. Andika nne katika nafasi ya mamia. Jibu la mstari wa pili linakuwa mia nne sitini.",
            "pg070_n0019": "Mistari miwili ya majibu ya muda sasa ni ishirini na tatu, na mia nne sitini.",
            "pg070_n0020": "Hatua ya tano. Jumlisha majibu ya muda: ishirini na tatu jumlisha mia nne sitini, sawa sawa na mia nne themanini na tatu. Maelezo ya njia iliyo upande wa kulia: ishirini na tatu ipo juu, ishirini na moja ipo chini ikiwa na alama ya kuzidisha. Chini yake kuna jibu la kwanza, ishirini na tatu. Mstari unaofuata una alama ya kujumlisha na mia nne sitini. Jumla ya mwisho ni mia nne themanini na tatu.",
            "pg070_n0021": "Kwa hiyo, ishirini na tatu kuzidisha ishirini na moja, sawa sawa na mia nne themanini na tatu.",
            "pg070_n0022": "Mfano wa Pili",
            "pg070_n0023": "Sabini na nane kuzidisha sitini na tisa, sawa sawa na ngapi? Njia ya mfano huu inaendelea katika ukurasa unaofuata.",
        },
    },
    71: {
        "rate": 0.85,
        "remove": {
            "pg071_n0003", "pg071_n0004", "pg071_n0005", "pg071_n0007", "pg071_n0008",
            "pg071_n0010", "pg071_n0011", "pg071_n0012", "pg071_n0014", "pg071_n0015", "pg071_n0026"
        },
        "replace": {
            "pg071_n0001": "Hatua na njia ya mfano wa pili kutoka ukurasa uliopita. Tendo ni sabini na nane kuzidisha sitini na tisa.",
            "pg071_n0002": "Hatua ya kwanza. Anza upande wa kulia. Zidisha mamoja nane kwa mamoja tisa. Nane kuzidisha tisa, sawa sawa na sabini na mbili. Andika mbili katika nafasi ya mamoja. Badili mamoja sabini kuwa makumi saba. Beba saba kwenda nafasi ya makumi.",
            "pg071_n0006": "Hatua ya pili. Zidisha tarakimu saba ya makumi kwa tarakimu tisa ya mamoja. Saba kuzidisha tisa, sawa sawa na sitini na tatu. Jumlisha makumi saba yaliyobebwa: saba jumlisha sitini na tatu, sawa sawa na sabini. Andika sifuri katika nafasi ya makumi na saba katika nafasi ya mamia. Jibu la muda la mstari wa kwanza ni mia saba na mbili.",
            "pg071_n0009": "Hatua ya tatu. Hamia tarakimu sita iliyo katika nafasi ya makumi ya kizidisho. Zidisha mamoja nane kwa tarakimu sita ya makumi. Nane kuzidisha sita, sawa sawa na arobaini na nane. Kwa sababu sita ipo katika nafasi ya makumi, andika sifuri katika nafasi ya mamoja na nane katika nafasi ya makumi. Badili makumi arobaini kuwa mamia manne. Beba nne kwenda nafasi ya mamia.",
            "pg071_n0013": "Hatua ya nne. Zidisha tarakimu saba ya makumi kwa tarakimu sita ya makumi. Saba kuzidisha sita, sawa sawa na arobaini na mbili. Jumlisha mamia manne yaliyobebwa: nne jumlisha arobaini na mbili, sawa sawa na arobaini na sita. Andika sita katika nafasi ya mamia na nne katika nafasi ya maelfu. Jibu la muda la mstari wa pili ni elfu nne mia sita themanini.",
            "pg071_n0016": "Hatua ya tano. Jumlisha majibu ya muda: mia saba na mbili, jumlisha elfu nne mia sita themanini, sawa sawa na elfu tano mia tatu themanini na mbili. Maelezo ya njia iliyo upande wa kulia: sabini na nane ipo juu. Sitini na tisa ipo chini ikiwa na alama ya kuzidisha. Mstari wa kwanza wa jibu ni mia saba na mbili. Mstari wa pili una alama ya kujumlisha na elfu nne mia sita themanini. Jumla ya mwisho ni elfu tano mia tatu themanini na mbili.",
            "pg071_n0017": "Kwa hiyo, sabini na nane kuzidisha sitini na tisa, sawa sawa na elfu tano mia tatu themanini na mbili.",
            "pg071_n0018": "Zoezi la Tatu",
            "pg071_n0020": "Swali namba moja. Ishirini na tatu kuzidisha kumi na tatu, sawa sawa na ngapi? Swali namba mbili. Thelathini na mbili kuzidisha thelathini na nne, sawa sawa na ngapi?",
            "pg071_n0021": "Swali namba tatu. Ishirini na mbili kuzidisha kumi na tatu, sawa sawa na ngapi? Swali namba nne. Hamsini na moja kuzidisha ishirini na mbili, sawa sawa na ngapi?",
            "pg071_n0022": "Swali namba tano. Hamsini na sita kuzidisha ishirini na tisa, sawa sawa na ngapi? Swali namba sita. Sabini na nne kuzidisha hamsini na tatu, sawa sawa na ngapi?",
            "pg071_n0023": "Swali namba saba. Arobaini na saba kuzidisha kumi na nane, sawa sawa na ngapi? Swali namba nane. Hamsini na tatu kuzidisha kumi na moja, sawa sawa na ngapi?",
            "pg071_n0024": "Swali namba tisa. Kumi na mbili kuzidisha ishirini na nne, sawa sawa na ngapi? Swali namba kumi. Themanini na tano kuzidisha sitini, sawa sawa na ngapi?",
            "pg071_n0025": "Swali namba kumi na moja. Mpangilio wa wima. Namba ya juu ni tisini na saba. Namba ya chini ni themanini na nane, ikiwa na alama ya kuzidisha. Tisini na saba kuzidisha themanini na nane, sawa sawa na ngapi? Swali namba kumi na mbili. Mpangilio wa wima. Namba ya juu ni themanini na nne. Namba ya chini ni tisini na tatu, ikiwa na alama ya kuzidisha. Themanini na nne kuzidisha tisini na tatu, sawa sawa na ngapi? Swali namba kumi na tatu. Mpangilio wa wima. Namba ya juu ni hamsini na sita. Namba ya chini ni ishirini na tatu, ikiwa na alama ya kuzidisha. Hamsini na sita kuzidisha ishirini na tatu, sawa sawa na ngapi?",
        },
    },
    72: {
        "rate": 0.85,
        "remove": {
            "pg072_n0002", "pg072_n0004", "pg072_n0006", "pg072_n0008",
            "pg072_n0013", "pg072_n0014", "pg072_n0015", "pg072_n0016", "pg072_n0017", "pg072_n0018",
            "pg072_n0020", "pg072_n0021", "pg072_n0022", "pg072_n0024",
        },
        "replace": {
            "pg072_n0001": "Swali namba kumi na nne. Ishirini na tisa kuzidisha thelathini na tatu, sawa sawa na ngapi? Swali namba kumi na tano. Arobaini na sita kuzidisha thelathini, sawa sawa na ngapi? Swali namba kumi na sita. Sitini na tano kuzidisha sabini na tano, sawa sawa na ngapi?",
            "pg072_n0003": "Swali namba kumi na saba. Ishirini kuzidisha kumi, sawa sawa na ngapi? Swali namba kumi na nane. Thelathini kuzidisha hamsini na moja, sawa sawa na ngapi? Swali namba kumi na tisa. Tisini na sita kuzidisha sabini na nane, sawa sawa na ngapi?",
            "pg072_n0005": "Swali namba ishirini. Kumi na tisa kuzidisha hamsini na tano, sawa sawa na ngapi?",
            "pg072_n0007": "Kuzidisha namba nzima zenye tarakimu tatu kwa kizidisho chenye tarakimu moja.",
            "pg072_n0009": "Mfano",
            "pg072_n0010": "Mia mbili kumi na saba kuzidisha nne, sawa sawa na ngapi? Mpangilio wa wima una mia mbili kumi na saba juu, na nne chini ya tarakimu saba katika nafasi ya mamoja, ikiwa na alama ya kuzidisha.",
            "pg072_n0011": "Hatua na njia. Hesabu inaanzia upande wa kulia, katika mamoja, kisha inaelekea kushoto.",
            "pg072_n0012": "Hatua ya kwanza. Zidisha mamoja saba kwa nne. Saba kuzidisha nne, sawa sawa na ishirini na nane. Andika nane katika nafasi ya mamoja. Badili mamoja ishirini kuwa makumi mawili. Beba makumi mawili kwenda nafasi ya makumi.",
            "pg072_n0019": "Hatua ya pili. Zidisha tarakimu moja ya makumi kwa nne. Moja kuzidisha nne, sawa sawa na nne. Jumlisha makumi mawili yaliyobebwa na makumi manne. Mbili jumlisha nne, sawa sawa na sita. Andika sita katika nafasi ya makumi.",
            "pg072_n0023": "Hatua ya tatu. Zidisha tarakimu mbili ya mamia kwa nne. Mbili kuzidisha nne, sawa sawa na nane. Andika nane katika nafasi ya mamia. Jibu la mpangilio wa wima ni mia nane sitini na nane.",
            "pg072_n0025": "Kwa hiyo, mia mbili kumi na saba kuzidisha nne, sawa sawa na mia nane sitini na nane.",
        },
    },
    73: {
        "rate": 0.85,
        "remove": {
            "pg073_n0004", "pg073_n0006", "pg073_n0008", "pg073_n0010", "pg073_n0012",
            "pg073_n0017", "pg073_n0019", "pg073_n0021", "pg073_n0023", "pg073_n0024",
        },
        "replace": {
            "pg073_n0001": "Zoezi la Nne",
            "pg073_n0002": "Jibu maswali yafuatayo.",
            "pg073_n0003": "Swali namba moja. Mia saba kumi kuzidisha tano, sawa sawa na ngapi? Swali namba mbili. Mia tatu arobaini na nane kuzidisha nane, sawa sawa na ngapi? Swali namba tatu. Mia mbili kumi na tatu kuzidisha sita, sawa sawa na ngapi?",
            "pg073_n0005": "Swali namba nne. Mia tano sabini na sita kuzidisha tatu, sawa sawa na ngapi? Swali namba tano. Mia moja hamsini na moja kuzidisha saba, sawa sawa na ngapi? Swali namba sita. Mia tatu na tano kuzidisha nne, sawa sawa na ngapi?",
            "pg073_n0007": "Swali namba saba. Mia mbili na tatu kuzidisha nane, sawa sawa na ngapi? Swali namba nane. Mia saba sitini kuzidisha mbili, sawa sawa na ngapi? Swali namba tisa. Mia mbili arobaini na tano kuzidisha tisa, sawa sawa na ngapi?",
            "pg073_n0009": "Swali namba kumi. Mia saba kumi na saba kuzidisha tisa, sawa sawa na ngapi? Swali namba kumi na moja. Mia sita na nane kuzidisha tano, sawa sawa na ngapi? Swali namba kumi na mbili. Mia moja kuzidisha nne, sawa sawa na ngapi?",
            "pg073_n0011": "Kuzidisha namba nzima zenye tarakimu tatu kwa kizidisho chenye tarakimu mbili.",
            "pg073_n0013": "Mfano",
            "pg073_n0014": "Mia sita ishirini na nne kuzidisha thelathini na tano, sawa sawa na ngapi?",
            "pg073_n0015": "Njia. Mpangilio wa wima una mia sita ishirini na nne juu na thelathini na tano chini, ikiwa na alama ya kuzidisha.",
            "pg073_n0016": "Hatua. Anza na tarakimu tano ya mamoja, kisha hamia tarakimu tatu ya makumi.",
            "pg073_n0018": "Hatua ya kwanza. Zidisha mia sita ishirini na nne kwa tano. Tano kuzidisha mia sita ishirini na nne, sawa sawa na elfu tatu mia moja ishirini. Andika jibu hilo katika mstari wa kwanza.",
            "pg073_n0020": "Hatua ya pili. Zidisha mia sita ishirini na nne kwa tarakimu tatu iliyo katika nafasi ya makumi. Tatu kuzidisha mia sita ishirini na nne ni elfu moja mia nane sabini na mbili; kwa kuwa tatu ni makumi matatu, jibu ni elfu kumi na nane mia saba ishirini. Andika jibu hilo katika mstari wa pili.",
            "pg073_n0022": "Hatua ya tatu. Jumlisha majibu ya muda. Elfu tatu mia moja ishirini, jumlisha elfu kumi na nane mia saba ishirini, sawa sawa na elfu ishirini na moja mia nane arobaini.",
            "pg073_n0025": "Kwa hiyo, mia sita ishirini na nne kuzidisha thelathini na tano, sawa sawa na elfu ishirini na moja mia nane arobaini.",
        },
    },
    74: {
        "rate": 0.85,
        "remove": {"pg074_n0007", "pg074_n0009", "pg074_n0013", "pg074_n0014", "pg074_n0017", "pg074_n0018"},
        "replace": {
            "pg074_n0001": "Zoezi la Tano",
            "pg074_n0002": "Jibu maswali yafuatayo.",
            "pg074_n0003": "Swali namba moja. Mia nne kumi na saba kuzidisha kumi na moja, sawa sawa na ngapi? Swali namba mbili. Mia moja thelathini kuzidisha sabini, sawa sawa na ngapi?",
            "pg074_n0004": "Swali namba tatu. Mia mbili tisini na mbili kuzidisha thelathini na saba, sawa sawa na ngapi? Swali namba nne. Mia tano na sita kuzidisha arobaini, sawa sawa na ngapi?",
            "pg074_n0005": "Swali namba tano. Mia tatu sitini na tano kuzidisha themanini na tano, sawa sawa na ngapi? Swali namba sita. Mia tisa kumi na sita kuzidisha hamsini na nane, sawa sawa na ngapi?",
            "pg074_n0006": "Swali namba saba. Mpangilio wa wima: mia saba hamsini na nane kuzidisha tisini na saba, sawa sawa na ngapi? Swali namba nane. Mpangilio wa wima: mia moja sabini na nne kuzidisha sitini na moja, sawa sawa na ngapi? Swali namba tisa. Mpangilio wa wima: mia tatu na sita kuzidisha arobaini na sita, sawa sawa na ngapi?",
            "pg074_n0008": "Swali namba kumi. Mpangilio wa wima: mia saba thelathini na saba kuzidisha themanini na tatu, sawa sawa na ngapi? Swali namba kumi na moja. Mpangilio wa wima: mia moja ishirini na nane kuzidisha sabini na saba, sawa sawa na ngapi? Swali namba kumi na mbili. Mpangilio wa wima: mia saba kuzidisha kumi, sawa sawa na ngapi?",
            "pg074_n0010": "Mafumbo yenye dhana ya kuzidisha namba nzima.",
            "pg074_n0011": "Mfano",
            "pg074_n0012": "Shule ya Msingi Katale ina madarasa tisa. Kila darasa lina wanafunzi thelathini na watano. Je, shule hiyo ina wanafunzi wangapi?",
            "pg074_n0015": "Njia. Idadi ya wanafunzi katika kila darasa ni thelathini na tano. Idadi ya madarasa ni tisa. Tendo ni thelathini na tano kuzidisha tisa.",
            "pg074_n0016": "Mpangilio wa wima una thelathini na tano juu na tisa chini ya tarakimu tano, ikiwa na alama ya kuzidisha. Thelathini na tano kuzidisha tisa, sawa sawa na mia tatu kumi na tano.",
            "pg074_n0019": "Kwa hiyo, Shule ya Msingi Katale ina wanafunzi mia tatu kumi na tano.",
        },
    },
    75: {
        "rate": 0.85,
        "remove": {"pg075_n0004", "pg075_n0005", "pg075_n0007", "pg075_n0008", "pg075_n0010", "pg075_n0013", "pg075_n0015", "pg075_n0016", "pg075_n0017", "pg075_n0019", "pg075_n0020", "pg075_n0022", "pg075_n0023", "pg075_n0024"},
        "replace": {
            "pg075_n0001": "Zoezi la Sita",
            "pg075_n0002": "Jibu maswali yafuatayo.",
            "pg075_n0003": "Swali namba moja. Lori la shule linabeba magunia sitini ya maharage kwa safari moja. Je, lori hilo litabeba magunia mangapi ya maharage katika safari kumi na tisa?",
            "pg075_n0006": "Swali namba mbili. Wastani wa watoto ishirini na wanane huzaliwa kwa mwezi katika Hospitali ya Mtakuja. Je, wastani wa watoto wangapi watazaliwa kwa kipindi cha miezi kumi na miwili?",
            "pg075_n0009": "Swali namba tatu. Kreti moja ya soda ina chupa ishirini na nne. Bei ya soda moja ni shilingi mia tano. Tafuta bei ya kreti moja ya soda.",
            "pg075_n0011": "Swali namba nne. Ipi ni kubwa zaidi: mia sita sabini na nane kuzidisha ishirini na tatu, au mia nne kumi kuzidisha thelathini na tisa?",
            "pg075_n0012": "Swali namba tano. Kiberiti kimoja hujazwa njiti thelathini na tano. Viberiti kumi vitajazwa jumla ya njiti ngapi?",
            "pg075_n0014": "Swali namba sita. Familia kumi na moja ziliahidi kuchangia mbao katika kampeni ya kuongeza idadi ya madawati shuleni. Ikiwa kila familia ilichangia mbao mia mbili na saba, je, zilipatikana jumla ya mbao ngapi?",
            "pg075_n0018": "Swali namba saba. Mfanyabiashara hupata faida ya shilingi hamsini na tano kwa kuuza kilogramu moja ya mchele. Je, atapata faida kiasi gani baada ya kuuza kilogramu mia tatu tisini na mbili za mchele?",
            "pg075_n0021": "Swali namba nane. Serikali ilitoa chakula cha msaada kwa kaya sabini na tatu zilizokumbwa na ukame. Iwapo kila kaya ilipewa kilogramu mia moja themanini za mahindi, je, serikali ilitoa jumla ya kilogramu ngapi za mahindi?",
        },
    },
    76: {
        "rate": 0.85,
        "remove": {"pg076_n0002", "pg076_n0003", "pg076_n0005", "pg076_n0006", "pg076_n0007", "pg076_n0010", "pg076_n0013"},
        "replace": {
            "pg076_n0001": "Swali namba tisa. Mfaume anafuga kuku tisini na wanane wa mayai. Iwapo kila kuku anataga mayai mawili kwa siku, je, kuku hao wanataga mayai mangapi kwa wiki moja?",
            "pg076_n0004": "Swali namba kumi. Ali ana bustani ya nyanya na karoti. Bustani ya nyanya ina vitalu thelathini; kila kitalu kimepandwa miche kumi na miwili. Bustani ya karoti ina vitalu kumi na tisa; kila kitalu kimepandwa miche kumi na mitano. Ali ana jumla ya miche mingapi katika bustani?",
            "pg076_n0008": "Jikumbushe",
            "pg076_n0009": "Jambo la kwanza. Unapozidisha namba, zipange katika mpangilio wa wima au ulalo.",
            "pg076_n0011": "Jambo la pili. Zidisha tarakimu kuanzia mamoja, kisha makumi, halafu mamia.",
            "pg076_n0012": "Jambo la tatu. Kizidisho ni namba inayotumiwa kuzidisha namba nyingine.",
            "pg076_n0014": "Jambo la nne. Namba yoyote ikizidishwa kwa sifuri, jibu lake ni sifuri.",
        },
    },
    77: {
        "rate": 0.85,
        "remove": {"pg077_n0006", "pg077_n0008", "pg077_n0009", "pg077_n0010", "pg077_n0016", "pg077_n0018"},
        "replace": {
            "pg077_n0001": "Sura ya Saba",
            "pg077_n0002": "Kugawanya namba nzima",
            "pg077_n0003": "Utangulizi",
            "pg077_n0004": "Dhana ya kugawanya ni sawa na kutoa kwa kujirudiarudia.",
            "pg077_n0005": "Katika sura hii, utajifunza kugawanya namba nzima zenye tarakimu hadi tatu kwa kigawanyo chenye tarakimu hadi mbili, bila baki.",
            "pg077_n0007": "Vilevile, utajifunza mafumbo yenye dhana ya kugawanya namba nzima. Katika maisha ya kila siku, ujuzi huu utakusaidia kugawa kwa usawa vitu kama fedha, mazao, daftari na mali mbalimbali.",
            "pg077_n0012": "Kugawanya vitu katika mafungu yaliyo sawa",
            "pg077_n0013": "Vitu hugawanywa kwa urahisi kwa kuviweka katika mafungu.",
            "pg077_n0014": "Kwa mfano, machungwa kumi yamegawanywa kwa usawa katika mafungu mawili kama ifuatavyo.",
            "pg077_n0015": "Maelezo ya picha. Upande wa kushoto kuna fungu moja lenye machungwa kumi, yaliyopangwa katika mistari mitatu: manne mstari wa kwanza, matatu mstari wa pili na matatu mstari wa tatu. Mshale unaelekea upande wa kulia. Upande wa kulia kuna mafungu mawili. Kila fungu lina machungwa matano, yaliyopangwa mawili, mawili, kisha moja. Hivyo, machungwa kumi kugawanya mafungu mawili, sawa sawa na machungwa matano katika kila fungu.",
            "pg077_n0017": "Kwa hiyo, machungwa kumi yamegawanywa kwa usawa katika mafungu mawili yenye machungwa matano kila moja.",
        },
    },
    78: {
        "rate": 0.85,
        "remove": {"pg078_n0005", "pg078_n0006", "pg078_n0008", "pg078_n0009", "pg078_n0010", "pg078_n0011", "pg078_n0017", "pg078_n0018", "pg078_n0020", "pg078_n0021"},
        "replace": {
            "pg078_n0001": "Mfano",
            "pg078_n0002": "Kimweli, Maimuna na Pendo wanataka kugawana pipi kumi na tano kwa usawa.",
            "pg078_n0003": "Je, kila mmoja atapata pipi ngapi?",
            "pg078_n0004": "Njia. Maelezo ya picha. Upande wa kushoto kuna fungu moja lenye pipi kumi na tano. Upande wa kulia kuna watu watatu: Kimweli, Maimuna na Pendo. Pipi zimegawanywa katika mafungu matatu yaliyo sawa; kila mtu ameoneshwa akiwa na pipi tano.",
            "pg078_n0007": "Unapogawanya vitu, ni vizuri kugawa kitu kimoja kimoja kwa awamu. Katika awamu ya kwanza, chukua pipi moja mpe Kimweli, pipi nyingine mpe Maimuna, na nyingine mpe Pendo. Endelea kwa awamu kwa mpangilio huo hadi pipi zote ziishe. Kisha hesabu pipi alizopata kila mmoja.",
            "pg078_n0013": "Kwa hiyo, kila mmoja atapata pipi tano.",
            "pg078_n0014": "Kazi",
            "pg078_n0015": "Chukua vihesabio mia mbili na kumi na uvitumie kufanya shughuli zifuatazo.",
            "pg078_n0016": "Swali namba moja. Chukua vihesabio thelathini kutoka katika vihesabio mia moja. Gawanya vihesabio hivyo thelathini katika mafungu sita yaliyo sawa. Je, umepata vihesabio vingapi kwa kila fungu?",
            "pg078_n0019": "Swali namba mbili. Chukua vihesabio themanini na vinne kutoka katika vihesabio mia moja. Gawanya vihesabio hivyo themanini na vinne katika mafungu kumi na mawili yaliyo sawa. Je, umepata vihesabio vingapi kwa kila fungu?",
        },
        "after": {
            "pg078_n0003": [],
        },
    },
    79: {
        "rate": 0.85,
        "remove": {"pg079_n0002", "pg079_n0003", "pg079_n0007", "pg079_n0008", "pg079_n0009", "pg079_n0012", "pg079_n0013", "pg079_n0014"},
        "replace": {
            "pg079_n0001": "Kazi, swali namba tatu. Chukua vihesabio tisini na sita kutoka katika vihesabio mia moja. Gawanya vihesabio hivyo tisini na sita katika mafungu matatu yaliyo sawa. Je, umepata vihesabio vingapi kwa kila fungu?",
            "pg079_n0004": "Zoezi la Kwanza",
            "pg079_n0005": "Jibu maswali yafuatayo.",
            "pg079_n0006": "Swali namba moja. Gawanya maembe katika mafungu matatu yenye idadi sawa. Kisha chora kwenye visanduku vilivyo wazi. Maelezo ya picha: fungu la mwanzo lina maembe kumi na tano, yaliyopangwa katika mistari mitano yenye maembe matatu kila mstari. Upande wa kulia kuna visanduku vitatu tupu vya mafungu matatu. Gawanya maembe kumi na tano katika mafungu matatu yaliyo sawa, bila kutaja jibu.",
            "pg079_n0010": "Je, kila fungu lina maembe mangapi?",
            "pg079_n0011": "Swali namba mbili. Gawanya nyanya katika mafungu mawili yenye idadi sawa. Kisha chora kwenye visanduku vilivyo wazi. Maelezo ya picha: fungu la mwanzo lina nyanya kumi na nane, zilizopangwa katika mistari sita yenye nyanya tatu kila mstari. Upande wa kulia kuna visanduku viwili tupu vya mafungu mawili. Gawanya nyanya kumi na nane katika mafungu mawili yaliyo sawa, bila kutaja jibu.",
            "pg079_n0015": "Je, kila fungu lina nyanya ngapi?",
        },
    },
    80: {
        "rate": 0.85,
        "remove": {"pg080_n0002", "pg080_n0003", "pg080_n0004", "pg080_n0007", "pg080_n0008", "pg080_n0009", "pg080_n0012", "pg080_n0013", "pg080_n0014"},
        "replace": {
            "pg080_n0001": "Swali namba tatu. Gawanya visoda katika mafungu matano yenye idadi sawa. Kisha chora kwenye visanduku vilivyo wazi. Maelezo ya picha: fungu la mwanzo lina visoda ishirini, vilivyopangwa katika mistari mitano yenye visoda vinne kila mstari. Upande wa kulia kuna visanduku vitano tupu vya mafungu matano. Gawanya visoda ishirini katika mafungu matano yaliyo sawa, bila kutaja jibu.",
            "pg080_n0005": "Je, kila fungu lina visoda vingapi?",
            "pg080_n0006": "Swali namba nne. Gawanya kuku katika mafungu matatu yaliyo sawa. Kisha chora kwenye visanduku vilivyo wazi. Maelezo ya picha: fungu la mwanzo lina kuku sita, waliopangwa katika mistari miwili yenye kuku watatu kila mstari. Upande wa kulia kuna visanduku vitatu tupu vya mafungu matatu. Gawanya kuku sita katika mafungu matatu yaliyo sawa, bila kutaja jibu.",
            "pg080_n0010": "Je, kila fungu lina kuku wangapi?",
            "pg080_n0011": "Swali namba tano. Gawanya mayai katika mafungu sita yenye idadi sawa. Kisha chora kwenye visanduku vilivyo wazi. Maelezo ya picha: fungu la mwanzo lina mayai kumi na nane, yaliyopangwa katika mistari sita yenye mayai matatu kila mstari. Upande wa kulia kuna visanduku sita tupu vya mafungu sita. Gawanya mayai kumi na nane katika mafungu sita yaliyo sawa, bila kutaja jibu.",
            "pg080_n0015": "Je, kila fungu lina mayai mangapi?",
        },
    },
    81: {
        "rate": 0.85,
        "remove": {"pg081_n0004", "pg081_n0006", "pg081_n0008", "pg081_n0010", "pg081_n0012"},
        "replace": {
            "pg081_n0001": "Zoezi la Pili",
            "pg081_n0002": "Jibu maswali yafuatayo.",
            "pg081_n0003": "Swali namba moja. Ukigawanya mapera kumi na manne katika mafungu saba yaliyo na idadi sawa, kila fungu litakuwa na mapera mangapi?",
            "pg081_n0005": "Swali namba mbili. Iwapo una maandazi ishirini na unataka kuyagawa kwa rafiki zako watano, kila mmoja atapata maandazi mangapi?",
            "pg081_n0007": "Swali namba tatu. Karoti thelathini zimepangwa katika mafungu kumi yenye idadi sawa. Je, kila fungu lina karoti ngapi?",
            "pg081_n0009": "Swali namba nne. Daftari arobaini na mbili ziligawiwa kwa watoto saba. Je, kila mtoto alipata daftari ngapi?",
            "pg081_n0011": "Swali namba tano. Chapati thelathini na sita ziligawiwa kwa watu kumi na wawili. Je, kila mmoja alipata chapati ngapi?",
            "pg081_n0013": "Kugawanya namba nzima",
            "pg081_n0014": "Kugawanya ni sawa na kutoa kwa kujirudiarudia.",
            "pg081_n0015": "Mfano",
            "pg081_n0016": "Ishirini kugawanya nne, sawa sawa na ngapi?",
            "pg081_n0017": "Hatua. Toa nne kwa kujirudiarudia hadi ufikie sifuri. Hesabu idadi ya hatua za kutoa.",
            "pg081_n0018": "Hatua ya kwanza. Ishirini kutoa nne, sawa sawa na kumi na sita.",
            "pg081_n0019": "Hatua ya pili. Kumi na sita kutoa nne, sawa sawa na kumi na mbili.",
            "pg081_n0020": "Hatua ya tatu. Kumi na mbili kutoa nne, sawa sawa na nane.",
            "pg081_n0021": "Hatua ya nne. Nane kutoa nne, sawa sawa na nne.",
            "pg081_n0022": "Hatua ya tano. Nne kutoa nne, sawa sawa na sifuri.",
            "pg081_n0023": "Tumetoa nne mara tano hadi kufikia sifuri. Hivyo, kuna makundi matano ya vitu vinne katika ishirini.",
            "pg081_n0024": "Kwa hiyo, ishirini kugawanya nne, sawa sawa na tano.",
        },
    },
    82: {
        "rate": 0.85,
        "remove": {"pg082_n0002", "pg082_n0007", "pg082_n0010", "pg082_n0012", "pg082_n0018", "pg082_n0022", "pg082_n0024", "pg082_n0025"},
        "replace": {
            "pg082_n0001": "Kugawanya namba nzima kwa njia fupi, kwa mpangilio wa ulalo.",
            "pg082_n0003": "Mfano wa Kwanza",
            "pg082_n0004": "Sitini na nane kugawanya mbili, sawa sawa na ngapi?",
            "pg082_n0005": "Njia",
            "pg082_n0006": "Unapogawanya namba, anza upande wa kushoto na uelekee kulia.",
            "pg082_n0008": "Hatua",
            "pg082_n0009": "Hatua ya kwanza. Gawanya makumi sita kwa mbili. Sita kugawanya mbili, sawa sawa na tatu. Hivyo unapata makumi matatu. Andika tarakimu tatu katika nafasi ya makumi ya jibu.",
            "pg082_n0011": "Hatua ya pili. Hamia kulia kwenye mamoja. Gawanya mamoja nane kwa mbili. Nane kugawanya mbili, sawa sawa na nne. Andika tarakimu nne katika nafasi ya mamoja, kulia kwa tarakimu tatu.",
            "pg082_n0013": "Kwa hiyo, sitini na nane kugawanya mbili, sawa sawa na thelathini na nne.",
            "pg082_n0014": "Mfano wa Pili",
            "pg082_n0015": "Mia mbili arobaini na tano kugawanya tano, sawa sawa na ngapi?",
            "pg082_n0016": "Njia",
            "pg082_n0017": "Anza upande wa kushoto na uelekee kulia.",
            "pg082_n0019": "Hatua",
            "pg082_n0020": "Hatua ya kwanza. Jaribu kugawanya tarakimu mbili ya mamia kwa tano. Mbili haitoshi kugawanywa kwa tano, kwa hiyo iunganishe na tarakimu nne iliyo upande wake wa kulia. Unapata ishirini na nne.",
            "pg082_n0021": "Hatua ya pili. Ishirini na nne kugawanya tano, sawa sawa na nne, na baki ni nne. Andika tarakimu nne katika nafasi ya kwanza ya jibu.",
            "pg082_n0023": "Hatua ya tatu. Leta chini tarakimu tano ya mwisho. Baki la nne linawakilisha makumi arobaini; liunganishe na mamoja matano ili kupata arobaini na tano. Arobaini na tano kugawanya tano, sawa sawa na tisa. Andika tarakimu tisa kulia kwa tarakimu nne.",
            "pg082_n0026": "Kwa hiyo, mia mbili arobaini na tano kugawanya tano, sawa sawa na arobaini na tisa.",
        },
    },
    84: {
        "remove": {"pg084_n0003", "pg084_n0013"},
        "replace": {
            "pg084_n0001": "Mfano wa Pili. Mchoro wa kugawanya kwa njia fupi unaonesha mia mbili arobaini kugawanya nane, sawa sawa na thelathini.",
            "pg084_n0002": "Hatua na njia.",
            "pg084_n0004": "Hatua ya Kwanza. Gawanya mbili kwa nane; haitoshelezi. Kwa hiyo, unganisha tarakimu mbili na tarakimu nne iliyo upande wake wa kulia.",
            "pg084_n0005": "Hatua ya Pili. Tarakimu hizo zinaunda ishirini na nne.",
            "pg084_n0006": "Ishirini na nne kugawanya nane ni tatu. Andika tatu katika nafasi ya jibu.",
            "pg084_n0007": "Njia upande wa mchoro sasa inaonesha tarakimu tatu juu ya ishirini na nne.",
            "pg084_n0008": "Hatua ya Tatu. Gawanya sifuri kwa nane; jibu ni sifuri.",
            "pg084_n0009": "Andika sifuri kulia kwa tatu. Jibu linakuwa thelathini.",
            "pg084_n0010": "Kwa hiyo, mia mbili arobaini kugawanya nane, sawa sawa na thelathini.",
            "pg084_n0011": "Mfano wa Tatu. Mchoro wa kugawanya kwa njia fupi unaonesha mia tatu themanini na nne kugawanya kumi na mbili, sawa sawa na thelathini na mbili.",
            "pg084_n0012": "Hatua na njia.",
            "pg084_n0014": "Hatua ya Kwanza. Gawanya tatu kwa kumi na mbili; haitoshelezi. Unganisha tatu na nane iliyo upande wake wa kulia ili kupata thelathini na nane.",
            "pg084_n0015": "Hatua ya Pili. Thelathini na nane kugawanya kumi na mbili ni tatu, na baki ni mbili.",
            "pg084_n0016": "Andika tatu katika nafasi ya jibu.",
            "pg084_n0017": "Hatua ya Tatu. Unganisha baki la mbili na tarakimu nne ili kupata ishirini na nne.",
            "pg084_n0018": "Ishirini na nne kugawanya kumi na mbili ni mbili.",
            "pg084_n0019": "Andika mbili kulia kwa tatu. Jibu linakuwa thelathini na mbili.",
            "pg084_n0020": "Kwa hiyo, mia tatu themanini na nne kugawanya kumi na mbili, sawa sawa na thelathini na mbili.",
            "pg084_n0021": "Zoezi la Nne",
            "pg084_n0023": "Swali namba 1. Sitini na nne kugawanya mbili, sawa sawa na ngapi? Swali namba 2. Tisini na tatu kugawanya tatu, sawa sawa na ngapi? Swali namba 3. Mia tisa tisini na tisa kugawanya tisa, sawa sawa na ngapi?",
            "pg084_n0024": "Swali namba 4. Mia nane arobaini kugawanya nne, sawa sawa na ngapi? Swali namba 5. Mia sita sitini kugawanya sita, sawa sawa na ngapi? Swali namba 6. Mia tatu sitini kugawanya kumi na nane, sawa sawa na ngapi?",
            "pg084_n0025": "Swali namba 7. Mia moja sitini na nane kugawanya nane, sawa sawa na ngapi? Swali namba 8. Mia nne kugawanya ishirini, sawa sawa na ngapi? Swali namba 9. Mia mbili kumi na saba kugawanya saba, sawa sawa na ngapi?",
            "pg084_n0026": "Swali namba 10. Mia tisa hamsini kugawanya tisini na tano, sawa sawa na ngapi? Swali namba 11. Sitini na nne kugawanya nne, sawa sawa na ngapi? Swali namba 12. Mia saba arobaini na nne kugawanya mbili, sawa sawa na ngapi?",
        },
    },
    85: {
        "rate": 0.85,
        "remove": {"pg085_n0011", "pg085_n0016", "pg085_n0018", "pg085_n0020", "pg085_n0021", "pg085_n0022", "pg085_n0024", "pg085_n0025"},
        "replace": {
            "pg085_n0001": "Swali namba kumi na tatu. Mia mbili sitini na nne kugawanya kumi na mbili, sawa sawa na ngapi? Swali namba kumi na nne. Mia tisa sitini na moja kugawanya thelathini na moja, sawa sawa na ngapi? Swali namba kumi na tano. Mia nane ishirini na tano kugawanya sabini na tano, sawa sawa na ngapi?",
            "pg085_n0002": "Swali namba kumi na sita. Mia nane arobaini kugawanya hamsini na sita, sawa sawa na ngapi? Swali namba kumi na saba. Mia tisa sitini kugawanya nane, sawa sawa na ngapi? Swali namba kumi na nane. Mia saba themanini kugawanya kumi na mbili, sawa sawa na ngapi?",
            "pg085_n0003": "Swali namba kumi na tisa. Mia saba thelathini na tano kugawanya ishirini na moja, sawa sawa na ngapi? Swali namba ishirini. Mia mbili tisini na nne kugawanya kumi na nne, sawa sawa na ngapi? Swali namba ishirini na moja. Mia tano sabini na nne kugawanya arobaini na moja, sawa sawa na ngapi?",
            "pg085_n0004": "Swali namba ishirini na mbili. Mia tano arobaini na nne kugawanya thelathini na mbili, sawa sawa na ngapi? Swali namba ishirini na tatu. Mia sita sabini na mbili kugawanya hamsini na sita, sawa sawa na ngapi? Swali namba ishirini na nne. Mia tano sitini na saba kugawanya ishirini na saba, sawa sawa na ngapi?",
            "pg085_n0005": "Swali namba ishirini na tano. Mia tatu tisini na sita kugawanya kumi na nane, sawa sawa na ngapi? Swali namba ishirini na sita. Mia mbili hamsini na tatu kugawanya kumi na moja, sawa sawa na ngapi? Swali namba ishirini na saba. Mia moja sabini kugawanya tano, sawa sawa na ngapi?",
            "pg085_n0006": "Swali namba ishirini na nane. Mia tisa kumi na nane kugawanya kumi na saba, sawa sawa na ngapi? Swali namba ishirini na tisa. Mia tatu na nane kugawanya kumi na nne, sawa sawa na ngapi? Swali namba thelathini. Mia mbili themanini na tano kugawanya kumi na tisa, sawa sawa na ngapi?",
            "pg085_n0007": "Swali namba thelathini na moja. Mia mbili kumi na sita kugawanya ishirini na nne, sawa sawa na ngapi? Swali namba thelathini na mbili. Mia nane themanini kugawanya kumi, sawa sawa na ngapi? Swali namba thelathini na tatu. Mia nne hamsini na moja kugawanya kumi na moja, sawa sawa na ngapi?",
            "pg085_n0008": "Swali namba thelathini na nne. Mia nne tisini na mbili kugawanya kumi na mbili, sawa sawa na ngapi? Swali namba thelathini na tano. Mia nne na nane kugawanya thelathini na nne, sawa sawa na ngapi? Swali namba thelathini na sita. Mia sita ishirini na nne kugawanya ishirini na sita, sawa sawa na ngapi?",
            "pg085_n0009": "Swali namba thelathini na saba. Mia tatu ishirini na mbili kugawanya ishirini na tatu, sawa sawa na ngapi? Swali namba thelathini na nane. Mia nne sitini na tano kugawanya kumi na tano, sawa sawa na ngapi? Swali namba thelathini na tisa. Mia mbili themanini na tisa kugawanya kumi na saba, sawa sawa na ngapi?",
            "pg085_n0010": "Kugawanya namba nzima kwa njia ndefu kwa kigawanyo chenye tarakimu moja, bila baki.",
            "pg085_n0012": "Mfano wa Kwanza",
            "pg085_n0013": "Sitini na nane kugawanya mbili, sawa sawa na ngapi? Katika alama ya njia ndefu, kigawanyo mbili kiko upande wa kushoto na kigawanywa sitini na nane kiko ndani ya alama.",
            "pg085_n0014": "Njia na hatua.",
            "pg085_n0015": "Hatua ya kwanza. Anza upande wa kushoto. Gawanya sita kwa mbili; unapata tatu. Andika tatu juu, katika nafasi ya kwanza ya jibu.",
            "pg085_n0017": "Hatua ya pili. Zidisha tatu kwa mbili. Tatu kuzidisha mbili, sawa sawa na sita. Andika sita chini ya sita. Toa: sita kutoa sita, sawa sawa na sifuri.",
            "pg085_n0019": "Hatua ya tatu. Shusha tarakimu nane. Gawanya nane kwa mbili; unapata nne.",
            "pg085_n0023": "Hatua ya nne. Andika nne kulia kwa tatu kwenye jibu. Zidisha nne kwa mbili. Nne kuzidisha mbili, sawa sawa na nane. Andika nane chini ya nane. Toa: nane kutoa nane, sawa sawa na sifuri.",
            "pg085_n0026": "Kwa hiyo, sitini na nane kugawanya mbili, sawa sawa na thelathini na nne.",
        },
    },
    86: {
        "rate": 0.85,
        "remove": {"pg086_n0002", "pg086_n0006", "pg086_n0008", "pg086_n0010", "pg086_n0012", "pg086_n0014", "pg086_n0016", "pg086_n0018", "pg086_n0021", "pg086_n0022"},
        "replace": {
            "pg086_n0001": "Mfano wa Pili",
            "pg086_n0003": "Njia. Mia nane na nane kugawanya nane, sawa sawa na ngapi? Katika alama ya njia ndefu, kigawanyo nane kiko kushoto na kigawanywa mia nane na nane kiko ndani ya alama.",
            "pg086_n0004": "Hatua.",
            "pg086_n0005": "Hatua ya kwanza. Anza na tarakimu nane ya mamia upande wa kushoto. Tafuta namba ambayo ikizidishwa kwa nane inatoa nane. Namba hiyo ni moja. Andika moja katika nafasi ya kwanza ya jibu. Moja kuzidisha nane, sawa sawa na nane. Andika nane chini ya nane. Toa: nane kutoa nane, sawa sawa na sifuri.",
            "pg086_n0007": "Mwisho wa hatua ya kwanza, tarakimu ya kwanza ya jibu ni moja.",
            "pg086_n0009": "Baki ni sifuri.",
            "pg086_n0011": "Hatua ya pili. Shusha tarakimu sifuri ya makumi. Sifuri kugawanya nane, sawa sawa na sifuri. Andika sifuri kulia kwa moja kwenye jibu.",
            "pg086_n0013": "Sifuri kuzidisha nane, sawa sawa na sifuri. Toa: sifuri kutoa sifuri, sawa sawa na sifuri.",
            "pg086_n0015": "Mwisho wa hatua ya pili, jibu la muda ni mia moja.",
            "pg086_n0017": "Baki ni sifuri.",
            "pg086_n0019": "Hatua ya tatu. Shusha tarakimu nane ya mwisho. Nane kugawanya nane, sawa sawa na moja. Andika moja kulia kwa sifuri kwenye jibu. Moja kuzidisha nane, sawa sawa na nane. Andika nane chini ya nane. Toa: nane kutoa nane, sawa sawa na sifuri.",
            "pg086_n0020": "Jibu lililo juu ya alama ya njia ndefu ni mia moja na moja.",
            "pg086_n0023": "Kwa hiyo, mia nane na nane kugawanya nane, sawa sawa na mia moja na moja.",
            "pg086_n0024": "Zoezi la Tano",
            "pg086_n0025": "Jibu maswali yafuatayo.",
            "pg086_n0026": "Swali namba moja. Themanini na sita kugawanya mbili. Swali namba mbili. Hamsini na tano kugawanya tano. Swali namba tatu. Themanini na nane kugawanya nne.",
            "pg086_n0027": "Swali namba nne. Mia saba ishirini na tatu kugawanya tatu. Swali namba tano. Mia tano thelathini na mbili kugawanya saba. Swali namba sita. Mia sita kugawanya nne.",
            "pg086_n0028": "Swali namba saba. Mia tisa kugawanya tano. Swali namba nane. Mia tatu hamsini na moja kugawanya tatu. Swali namba tisa. Mia sita sitini kugawanya sita.",
            "pg086_n0029": "Swali namba kumi. Mia moja themanini na tisa kugawanya saba. Swali namba kumi na moja. Mia moja themanini na nne kugawanya nne. Swali namba kumi na mbili. Mia saba thelathini na sita kugawanya nane.",
            "pg086_n0030": "Swali namba kumi na tatu. Mia moja ishirini na sita kugawanya tisa. Swali namba kumi na nne. Mia saba themanini na tatu kugawanya tatu. Swali namba kumi na tano. Mia saba kugawanya tano.",
            "pg086_n0031": "Swali namba kumi na sita. Mia nane ishirini na nne kugawanya nane. Swali namba kumi na saba. Mia sita sitini na tano kugawanya saba. Swali namba kumi na nane. Mia nane arobaini na saba kugawanya saba.",
            "pg086_n0032": "Swali namba kumi na tisa. Mia saba sitini na tano kugawanya tisa. Swali namba ishirini. Mia mbili ishirini na nane kugawanya sita. Swali namba ishirini na moja. Mia sita hamsini na tano kugawanya tano.",
            "pg086_n0033": "Swali namba ishirini na mbili. Mia nne tisini na tano kugawanya tatu. Swali namba ishirini na tatu. Mia moja kumi na nne kugawanya sita. Swali namba ishirini na nne. Mia tano sabini na sita kugawanya nne.",
        },
    },
    87: {
        "rate": 0.85,
        "remove": {"pg087_n0004", "pg087_n0006", "pg087_n0008", "pg087_n0010", "pg087_n0012", "pg087_n0014", "pg087_n0015", "pg087_n0017", "pg087_n0018", "pg087_n0019", "pg087_n0022", "pg087_n0023", "pg087_n0025", "pg087_n0027", "pg087_n0029", "pg087_n0031", "pg087_n0033", "pg087_n0034", "pg087_n0036", "pg087_n0037"},
        "replace": {
            "pg087_n0001": "Kugawanya namba nzima kwa njia ndefu kwa kigawanyo chenye tarakimu mbili, bila baki.",
            "pg087_n0003": "Mfano wa Kwanza. Mia nne hamsini na moja kugawanya kumi na moja, sawa sawa na ngapi?",
            "pg087_n0005": "Hatua ya kwanza. Gawanya tarakimu nne kwa kumi na moja; haitoshi. Unganisha nne na tano ili kupata arobaini na tano.",
            "pg087_n0007": "Hatua ya pili. Tafuta namba ambayo ikizidishwa kwa kumi na moja inatoa arobaini na tano au pungufu. Kumi na moja kuzidisha nne, sawa sawa na arobaini na nne.",
            "pg087_n0009": "Andika nne katika nafasi ya kwanza ya jibu.",
            "pg087_n0011": "Hatua ya tatu. Andika arobaini na nne chini ya arobaini na tano. Toa: arobaini na tano kutoa arobaini na nne, sawa sawa na moja.",
            "pg087_n0013": "Hatua ya nne. Shusha tarakimu moja ya mwisho, kulia kwa baki la moja. Unapata kumi na moja.",
            "pg087_n0016": "Hatua ya tano. Kumi na moja kugawanya kumi na moja, sawa sawa na moja. Andika moja kulia kwa nne kwenye jibu. Moja kuzidisha kumi na moja, sawa sawa na kumi na moja. Toa: kumi na moja kutoa kumi na moja, sawa sawa na sifuri.",
            "pg087_n0020": "Kwa hiyo, mia nne hamsini na moja kugawanya kumi na moja, sawa sawa na arobaini na moja.",
            "pg087_n0021": "Mfano wa Pili. Mia sita themanini na nne kugawanya kumi na nane, sawa sawa na ngapi?",
            "pg087_n0024": "Hatua ya kwanza. Gawanya tarakimu sita kwa kumi na nane; haitoshi. Unganisha sita na nane ili kupata sitini na nane.",
            "pg087_n0026": "Hatua ya pili. Tafuta namba ambayo ikizidishwa kwa kumi na nane inatoa sitini na nane au pungufu. Kumi na nane kuzidisha tatu, sawa sawa na hamsini na nne.",
            "pg087_n0028": "Hatua ya tatu. Andika tatu katika nafasi ya kwanza ya jibu. Andika hamsini na nne chini ya sitini na nane. Toa: sitini na nane kutoa hamsini na nne, sawa sawa na kumi na nne.",
            "pg087_n0030": "Baki ni kumi na nne.",
            "pg087_n0032": "Hatua ya nne. Shusha tarakimu nne ya mwisho, kulia kwa baki la kumi na nne. Unapata mia moja arobaini na nne.",
            "pg087_n0035": "Hatua ya tano. Mia moja arobaini na nne kugawanya kumi na nane, sawa sawa na nane. Andika nane kulia kwa tatu kwenye jibu. Nane kuzidisha kumi na nane, sawa sawa na mia moja arobaini na nne. Toa: mia moja arobaini na nne kutoa mia moja arobaini na nne, sawa sawa na sifuri.",
            "pg087_n0038": "Kwa hiyo, mia sita themanini na nne kugawanya kumi na nane, sawa sawa na thelathini na nane.",
        },
    },
    88: {
        "rate": 0.85,
        "remove": {"pg088_n0014", "pg088_n0015", "pg088_n0019", "pg088_n0020"},
        "replace": {
            "pg088_n0001": "Zoezi la Sita",
            "pg088_n0002": "Jibu maswali yafuatayo.",
            "pg088_n0003": "Swali namba moja. Mia tisa ishirini na nne kugawanya themanini na nne. Swali namba mbili. Mia moja sitini na tisa kugawanya kumi na tatu. Swali namba tatu. Mia moja tisini na mbili kugawanya kumi na mbili.",
            "pg088_n0004": "Swali namba nne. Mia sita sitini na tatu kugawanya kumi na saba. Swali namba tano. Mia tano sabini na tano kugawanya ishirini na tatu. Swali namba sita. Mia sita kugawanya hamsini.",
            "pg088_n0005": "Swali namba saba. Mia tisa kugawanya kumi na tano. Swali namba nane. Mia tatu hamsini na moja kugawanya kumi na tatu. Swali namba tisa. Mia tano ishirini na tano kugawanya ishirini na tano.",
            "pg088_n0006": "Swali namba kumi. Mia tano hamsini na mbili kugawanya ishirini na tatu. Swali namba kumi na moja. Mia saba sitini na nane kugawanya thelathini na mbili. Swali namba kumi na mbili. Mia saba kumi na nne kugawanya kumi na saba.",
            "pg088_n0007": "Swali namba kumi na tatu. Mia tano na nne kugawanya kumi na nne. Swali namba kumi na nne. Mia saba themanini na mbili kugawanya thelathini na nne. Swali namba kumi na tano. Mia saba kugawanya ishirini na tano.",
            "pg088_n0008": "Swali namba kumi na sita. Mia mbili themanini na nane kugawanya kumi na sita. Swali namba kumi na saba. Mia sita sabini na tano kugawanya ishirini na saba. Swali namba kumi na nane. Mia nne kumi na nane kugawanya ishirini na mbili.",
            "pg088_n0009": "Swali namba kumi na tisa. Mia saba sabini na tano kugawanya thelathini na moja. Swali namba ishirini. Mia tatu ishirini kugawanya kumi na sita. Swali namba ishirini na moja. Mia tatu sabini na tano kugawanya kumi na tano.",
            "pg088_n0010": "Swali namba ishirini na mbili. Mia nne tisini na tano kugawanya thelathini na tatu. Swali namba ishirini na tatu. Mia tatu sabini na nne kugawanya kumi na saba. Swali namba ishirini na nne. Mia sita kugawanya ishirini na nne.",
            "pg088_n0011": "Mafumbo yenye dhana ya kugawanya namba nzima.",
            "pg088_n0012": "Mfano wa Kwanza",
            "pg088_n0013": "Kitabu cha hadithi kina kurasa mia moja hamsini na sita. Baraka anaweza kusoma kurasa kumi na mbili kila siku. Je, atatumia siku ngapi kusoma kitabu chote?",
            "pg088_n0016": "Njia.",
            "pg088_n0017": "Gawanya idadi ya kurasa zote, mia moja hamsini na sita, kwa kurasa kumi na mbili anazosoma kila siku.",
            "pg088_n0018": "Tendo ni mia moja hamsini na sita kugawanya kumi na mbili. Kwa njia fupi, jibu ni kumi na tatu.",
            "pg088_n0021": "Kwa hiyo, Baraka atatumia siku kumi na tatu kusoma kitabu chote.",
        },
    },
    89: {
        "rate": 0.85,
        "remove": {"pg089_n0003", "pg089_n0008", "pg089_n0009", "pg089_n0010", "pg089_n0011", "pg089_n0012", "pg089_n0013", "pg089_n0018", "pg089_n0020", "pg089_n0022", "pg089_n0024"},
        "replace": {
            "pg089_n0001": "Mfano wa Pili",
            "pg089_n0002": "Wanafunzi ishirini na wanne waligawana machungwa mia tisa themanini na manne kwa idadi sawa. Kila mwanafunzi alipata machungwa mangapi?",
            "pg089_n0004": "Njia.",
            "pg089_n0005": "Gawanya machungwa mia tisa themanini na manne kwa wanafunzi ishirini na wanne ili kupata idadi ya machungwa kwa kila mwanafunzi.",
            "pg089_n0006": "Tendo ni mia tisa themanini na nne kugawanya ishirini na nne.",
            "pg089_n0007": "Kwa njia ndefu: ishirini na nne inaingia katika tisini na nane mara nne. Ishirini na nne kuzidisha nne, sawa sawa na tisini na sita. Tisini na nane kutoa tisini na sita, sawa sawa na mbili. Shusha nne ili kupata ishirini na nne. Ishirini na nne kugawanya ishirini na nne, sawa sawa na moja. Jibu ni arobaini na moja.",
            "pg089_n0014": "Kwa hiyo, kila mwanafunzi alipata machungwa arobaini na moja.",
            "pg089_n0015": "Zoezi la Saba",
            "pg089_n0016": "Jibu maswali yafuatayo.",
            "pg089_n0017": "Swali namba moja. Muoka mikate alipata shilingi elfu nane baada ya kuuza mikate nane. Je, kila mkate uliuzwa kwa kiasi gani?",
            "pg089_n0019": "Swali namba mbili. Mama Maganga aliuza mayai sita kwa shilingi mia tisa sitini. Yai moja liliuzwa kwa shilingi ngapi?",
            "pg089_n0021": "Swali namba tatu. Chupa mia tano sitini za soda zilipakiwa kwenye kreti kumi na nne. Je, kila kreti ilipakiwa chupa ngapi?",
            "pg089_n0023": "Swali namba nne. Treni ilibeba abiria mia tano sabini na tisa katika safari tatu, kwa idadi sawa ya abiria. Abiria wangapi walibebwa katika kila safari?",
        },
    },
    90: {
        "rate": 0.85,
        "remove": {"pg090_n0002", "pg090_n0004", "pg090_n0005", "pg090_n0007", "pg090_n0010", "pg090_n0012", "pg090_n0013", "pg090_n0017"},
        "replace": {
            "pg090_n0001": "Swali namba tano. Karatasi kumi na tano za kuandikia zina jumla ya mistari mia moja tisini na tano. Kila karatasi ina mistari mingapi?",
            "pg090_n0003": "Swali namba sita. Shule ya Msingi Majengo ina wanafunzi mia nane tisini na saba na madarasa ishirini na matatu. Iwapo idadi ya wanafunzi ni sawa kwa kila darasa, je, kila darasa lina wanafunzi wangapi?",
            "pg090_n0006": "Swali namba saba. Boksi moja lina miche ya sabuni ishirini na mitano. Yatahitajika maboksi mangapi kwa miche ya sabuni mia tisa?",
            "pg090_n0008": "Swali namba nane. Bei ya pipi kumi na moja ni shilingi mia nne arobaini. Tafuta bei ya pipi moja.",
            "pg090_n0009": "Swali namba tisa. Malori kumi na tisa ya aina moja yana magurudumu mia moja kumi na manne. Je, kila lori lina magurudumu mangapi?",
            "pg090_n0011": "Swali namba kumi. Kamba yenye urefu wa sentimita mia tatu imegawanywa katika vipande kumi vilivyo sawa. Je, kila kipande kina urefu wa sentimita ngapi?",
            "pg090_n0014": "Jikumbushe",
            "pg090_n0015": "Jambo la kwanza. Unapogawanya vitu, gawa kitu kimoja kimoja kwa awamu.",
            "pg090_n0016": "Jambo la pili. Kugawanya namba ni sawa na kutoa namba kwa kujirudiarudia.",
        },
    },
    91: {
        "rate": 0.85,
        "remove": {"pg091_n0005", "pg091_n0006", "pg091_n0007", "pg091_n0008", "pg091_n0009", "pg091_n0010", "pg091_n0011", "pg091_n0012", "pg091_n0016", "pg091_n0017"},
        "replace": {
            "pg091_n0001": "Sura ya Nane",
            "pg091_n0002": "Sehemu",
            "pg091_n0003": "Utangulizi",
            "pg091_n0004": "Vitu halisi huweza kugawanywa katika vipande. Vipande hivyo huitwa sehemu. Ulipokuwa mwaka wa kwanza ulijifunza kugawa vitu katika sehemu, kwa mfano robo, nusu na theluthi. Vilevile, ulijifunza kusoma na kuandika sehemu hizo. Katika sura hii utaendelea kujifunza kusoma na kuandika sehemu zenye asili mbalimbali. Pia utajifunza kujumlisha na kutoa sehemu zenye asili moja. Katika maisha, elimu ya sehemu hutumika katika kuuza na kununua, kupanga wanafunzi na matokeo darasani, na kugawanya vitu.",
            "pg091_n0013": "Zoezi la Kwanza: Marudio",
            "pg091_n0014": "Jibu maswali yafuatayo.",
            "pg091_n0015": "Swali namba moja. Ni sehemu gani ya kila umbo imetiwa kivuli? Maelezo ya mchoro bila kutaja majibu. Sehemu a ina maduara matatu yaliyo katika mstari; duara moja limetiwa kivuli. Sehemu b ina duara lililogawanywa katika vipande vinne vilivyo sawa; kipande kimoja kimetiwa kivuli. Sehemu c ina duara lililogawanywa katika vipande vitatu vilivyo sawa; kipande kimoja kimetiwa kivuli. Sehemu d ina mstatili uliogawanywa katika vipande viwili vilivyo sawa; kipande kimoja kimetiwa kivuli. Taja sehemu iliyotiwa kivuli katika kila mchoro.",
        },
    },
    92: {
        "rate": 0.85,
        "remove": {"pg092_n0002", "pg092_n0003", "pg092_n0005", "pg092_n0006"},
        "replace": {
            "pg092_n0001": "Swali namba mbili. Musa alikata chungwa katika vipande viwili vilivyo sawa. Alimpa dada yake Neema kipande kimoja. Je, kila mmoja alipata sehemu gani ya chungwa?",
            "pg092_n0004": "Swali namba tatu. Mwalimu ana muwa wenye pingili nne zilizo sawa. Anataka kuwagawia wanafunzi wanne, kila mmoja kipande kimoja. Je, kila mwanafunzi atapata kipande kimoja kati ya vingapi?",
        },
    },
    93: {
        "rate": 0.85,
        "remove": {"pg093_n0002", "pg093_n0003", "pg093_n0004", "pg093_n0006", "pg093_n0007", "pg093_n0010", "pg093_n0011", "pg093_n0013", "pg093_n0014", "pg093_n0015", "pg093_n0016", "pg093_n0017", "pg093_n0018", "pg093_n0019", "pg093_n0021", "pg093_n0023", "pg093_n0024", "pg093_n0025", "pg093_n0026", "pg093_n0027", "pg093_n0028", "pg093_n0029", "pg093_n0031"},
        "replace": {
            "pg093_n0001": "Swali namba nne. Selemani alikuwa na papai moja. Alipokutana na rafiki zake Doto na Kulwa, aliamua wagawane papai hilo katika vipande vilivyo sawa. Je, Selemani alibakiwa na sehemu gani ya papai hilo?",
            "pg093_n0005": "Swali namba tano. Khadija ana fungu moja la machungwa mawili. Anataka kuwapa watoto wawili, kila mmoja chungwa moja. Kila mtoto atapata sehemu gani ya fungu la machungwa?",
            "pg093_n0008": "Kusoma na kuandika sehemu zenye asili mbalimbali.",
            "pg093_n0009": "Vitu mbalimbali vinaweza kugawanywa katika sehemu au makundi yaliyo sawa. Sehemu hizo zinaweza kuwasilishwa kwa vipande katika maumbo, kama michoro ifuatayo inavyoonesha.",
            "pg093_n0012": "Mfano wa kwanza. Mchoro una duara moja lililogawanywa katika vipande vinne vilivyo sawa. Vipande vyote vinne vimetiwa kivuli. Sehemu iliyotiwa kivuli ni vipande vinne kati ya vipande vinne.",
            "pg093_n0020": "Hii huandikwa nne kwa nne.",
            "pg093_n0022": "Mfano wa pili. Mchoro una duara moja lililogawanywa katika vipande vitano vilivyo sawa. Kipande kimoja kimetiwa kivuli. Sehemu iliyotiwa kivuli ni kipande kimoja kati ya vipande vitano.",
            "pg093_n0030": "Hii huandikwa moja kwa tano.",
        },
    },
    94: {
        "rate": 0.85,
        "remove": {"pg094_n0002", "pg094_n0003", "pg094_n0004", "pg094_n0005", "pg094_n0006", "pg094_n0007", "pg094_n0008", "pg094_n0010", "pg094_n0012", "pg094_n0013", "pg094_n0014", "pg094_n0015", "pg094_n0016", "pg094_n0017", "pg094_n0018", "pg094_n0020", "pg094_n0022", "pg094_n0023", "pg094_n0024", "pg094_n0026"},
        "replace": {
            "pg094_n0001": "Mfano wa tatu. Mchoro una kitu kizima kimoja kilichogawanywa katika vipande nane vilivyo sawa. Vipande vitatu vimetiwa kivuli. Sehemu iliyotiwa kivuli ni vipande vitatu kati ya vipande nane.",
            "pg094_n0009": "Hii huandikwa tatu kwa nane.",
            "pg094_n0011": "Mfano wa nne. Mchoro una kitu kizima kimoja kilichogawanywa katika vipande vitatu vilivyo sawa. Vipande viwili vimetiwa kivuli. Sehemu iliyotiwa kivuli ni vipande viwili kati ya vipande vitatu.",
            "pg094_n0019": "Hii huandikwa mbili kwa tatu.",
            "pg094_n0021": "Mfano wa tano. Mchoro una kitu kizima kimoja kilichogawanywa katika vipande tisa vilivyo sawa. Kipande kimoja kimetiwa kivuli. Sehemu iliyotiwa kivuli ni kipande kimoja kati ya vipande tisa.",
            "pg094_n0025": "Hii huandikwa moja kwa tisa.",
        },
    },
    95: {
        "rate": 0.85,
        "remove": {"pg095_n0004", "pg095_n0005", "pg095_n0006", "pg095_n0007", "pg095_n0008", "pg095_n0015", "pg095_n0016", "pg095_n0017", "pg095_n0018", "pg095_n0020", "pg095_n0021", "pg095_n0022", "pg095_n0023", "pg095_n0024", "pg095_n0025"},
        "replace": {
            "pg095_n0001": "Zoezi la Pili",
            "pg095_n0002": "Jibu maswali yafuatayo.",
            "pg095_n0003": "Swali namba moja. Andika kwa maneno sehemu zifuatazo. Sehemu a, moja kwa sita. Sehemu b, nane kwa kumi. Sehemu c, tatu kwa nne. Sehemu d, saba kwa kumi na moja.",
            "pg095_n0009": "Swali namba mbili. Andika sehemu zifuatazo kwa tarakimu.",
            "pg095_n0010": "Sehemu a. Mbili ya saba. Andika kwa tarakimu katika nafasi iliyo wazi.",
            "pg095_n0011": "Sehemu b. Nne ya tisa. Andika kwa tarakimu katika nafasi iliyo wazi.",
            "pg095_n0012": "Sehemu c. Moja ya kumi na mbili. Andika kwa tarakimu katika nafasi iliyo wazi.",
            "pg095_n0013": "Sehemu d. Sita ya tisa. Andika kwa tarakimu katika nafasi iliyo wazi.",
            "pg095_n0014": "Swali namba tatu. Chora duara, kisha ligawanye na utie kivuli kuonesha sehemu zifuatazo. Sehemu a, mbili kwa nne. Sehemu b, tatu kwa saba. Sehemu c, tano kwa tano. Sehemu d, nne kwa sita.",
            "pg095_n0019": "Swali namba nne. Tia kivuli katika mchoro a hadi d kuonesha sehemu husika. Sehemu a ni mbili kwa nne. Mchoro una visanduku vinne vilivyo sawa, havijatiwa kivuli. Sehemu b ni sita kwa nane. Mchoro una duara lililogawanywa katika vipande nane vilivyo sawa, hakuna kipande kilichotiwa kivuli. Sauti inaeleza mpangilio wa michoro bila kutia kivuli kwa niaba ya mwanafunzi.",
        },
    },
    96: {
        "rate": 0.85,
        "remove": {"pg096_n0001", "pg096_n0002", "pg096_n0003", "pg096_n0004", "pg096_n0005", "pg096_n0006", "pg096_n0009", "pg096_n0010", "pg096_n0012", "pg096_n0014", "pg096_n0019", "pg096_n0020", "pg096_n0021", "pg096_n0026"},
        "replace": {
            "pg096_n0007": "Muendelezo wa swali namba nne kutoka ukurasa uliopita. Sehemu c, tatu kwa tano. Sehemu d, tano kwa kumi na mbili. Kujumlisha sehemu zenye asili moja.",
            "pg096_n0008": "Unaweza kujumlisha sehemu zenye asili moja kwa kutumia michoro, mstari wa namba na namba. Katika sehemu, namba iliyo juu ya mstari huitwa kiasi; namba iliyo chini ya mstari huitwa asili.",
            "pg096_n0011": "Mfano wa Kwanza",
            "pg096_n0013": "Katika sehemu moja kwa tatu, andika kiasi na asili.",
            "pg096_n0015": "Jibu.",
            "pg096_n0016": "Katika sehemu moja kwa tatu, moja ni kiasi na tatu ni asili.",
            "pg096_n0017": "Mfano wa Pili",
            "pg096_n0018": "Tumia michoro kujibu swali lifuatalo. Tatu kwa nne, jumlisha moja kwa nne, sawa sawa na ngapi?",
            "pg096_n0022": "Hatua.",
            "pg096_n0023": "Hatua ya kwanza. Chora duara mbili zinazolingana.",
            "pg096_n0024": "Hatua ya pili. Gawanya kila duara katika sehemu nne zinazolingana.",
            "pg096_n0025": "Hatua ya tatu. Weka kivuli katika sehemu tatu kati ya sehemu nne kwenye duara la kwanza.",
        },
    },
    97: {
        "rate": 0.85,
        "remove": {"pg097_n0005", "pg097_n0008", "pg097_n0009", "pg097_n0010", "pg097_n0011", "pg097_n0013", "pg097_n0014", "pg097_n0015", "pg097_n0016", "pg097_n0018", "pg097_n0021", "pg097_n0022", "pg097_n0023", "pg097_n0028"},
        "replace": {
            "pg097_n0001": "Hatua ya nne. Andika sehemu iliyotiwa kivuli kwa tarakimu: tatu kwa nne.",
            "pg097_n0002": "Hatua ya tano. Weka kivuli katika sehemu moja kati ya nne kwenye duara la pili.",
            "pg097_n0003": "Hatua ya sita. Andika sehemu iliyotiwa kivuli kwa tarakimu: moja kwa nne.",
            "pg097_n0004": "Hatua ya saba. Hesabu idadi ya sehemu zilizotiwa kivuli katika duara zote mbili.",
            "pg097_n0006": "Hatua ya nane. Andika sehemu iliyopatikana kwa tarakimu.",
            "pg097_n0007": "Hatua ya tisa. Chora duara la tatu kuonesha jibu.",
            "pg097_n0012": "Jibu ni duara moja lililogawanywa katika sehemu nne zilizo sawa, na sehemu zote nne zimetiwa kivuli.",
            "pg097_n0017": "Kwa hiyo, tatu kwa nne jumlisha moja kwa nne, sawa sawa na nne kwa nne.",
            "pg097_n0019": "Mfano wa Tatu",
            "pg097_n0020": "Tumia mstari wa namba kujibu swali lifuatalo. Tano kwa nane jumlisha mbili kwa nane, sawa sawa na ngapi?",
            "pg097_n0024": "Hatua.",
            "pg097_n0025": "Hatua ya kwanza. Chora mstari, kisha ugawanye katika vipande nane vinavyolingana.",
            "pg097_n0026": "Hatua ya pili. Weka alama kwenye kila kipande.",
            "pg097_n0027": "Hatua ya tatu. Ukianzia sifuri, alama ya kwanza kulia ni moja kwa nane. Endelea kuweka alama hadi nane kwa nane.",
            "pg097_n0029": "Hatua ya nne. Anza kwenye sifuri, kisha nenda hatua tano kulia.",
        },
    },
    98: {
        "rate": 0.85,
        "remove": {"pg098_n0003", "pg098_n0004", "pg098_n0005", "pg098_n0006", "pg098_n0007", "pg098_n0008", "pg098_n0009", "pg098_n0011", "pg098_n0012", "pg098_n0014", "pg098_n0015", "pg098_n0016", "pg098_n0019", "pg098_n0021", "pg098_n0023", "pg098_n0026", "pg098_n0028", "pg098_n0029", "pg098_n0031"},
        "replace": {
            "pg098_n0001": "Maelezo ya mchoro wa mstari wa namba. Mstari unaanzia sifuri na umegawanywa katika sehemu nane sawa, kuanzia moja kwa nane hadi nane kwa nane. Hatua ya tano. Kutoka kwenye tano kwa nane, nenda hatua mbili zaidi kulia.",
            "pg098_n0002": "Hatua ya sita. Soma sehemu ilipo hatua ya mwisho. Umefika saba kwa nane.",
            "pg098_n0010": "Kwa hiyo, tano kwa nane jumlisha mbili kwa nane, sawa sawa na saba kwa nane.",
            "pg098_n0013": "Mfano wa Nne",
            "pg098_n0017": "Tendo ni kumi na tatu kwa ishirini na saba, jumlisha saba kwa ishirini na saba. Hatua.",
            "pg098_n0018": "Hatua ya kwanza. Jumlisha namba za kiasi kama unavyojumlisha namba za kawaida. Kumi na tatu jumlisha saba, sawa sawa na ishirini.",
            "pg098_n0020": "Hatua ya pili. Asili haibadiliki; inabaki ishirini na saba.",
            "pg098_n0022": "Hatua ya tatu. Kwa hiyo, kumi na tatu kwa ishirini na saba jumlisha saba kwa ishirini na saba, sawa sawa na ishirini kwa ishirini na saba.",
            "pg098_n0024": "Zoezi la Tatu",
            "pg098_n0025": "Jibu maswali yafuatayo.",
            "pg098_n0027": "Swali namba moja. Mbili kwa tano jumlisha mbili kwa tano. Swali namba mbili. Tatu kwa tisa jumlisha tano kwa tisa. Swali namba tatu. Moja kwa nne jumlisha moja kwa nne.",
            "pg098_n0030": "Swali namba nne. Tatu kwa sita jumlisha mbili kwa sita. Swali namba tano. Moja kwa tano jumlisha mbili kwa tano. Swali namba sita. Tano kwa nane jumlisha moja kwa nane.",
        },
    },
    99: {
        "rate": 0.85,
        "remove": {"pg099_n0001", "pg099_n0003", "pg099_n0004", "pg099_n0006", "pg099_n0007", "pg099_n0009", "pg099_n0010", "pg099_n0012", "pg099_n0013", "pg099_n0015", "pg099_n0018", "pg099_n0020", "pg099_n0023", "pg099_n0025", "pg099_n0026", "pg099_n0028", "pg099_n0029", "pg099_n0031", "pg099_n0032", "pg099_n0034"},
        "replace": {
            "pg099_n0002": "Swali namba saba. Tatu kwa kumi jumlisha tano kwa kumi. Swali namba nane. Moja kwa saba jumlisha tano kwa saba. Swali namba tisa. Moja kwa mbili jumlisha moja kwa mbili.",
            "pg099_n0005": "Swali namba kumi. Mbili kwa sita jumlisha nne kwa sita. Swali namba kumi na moja. Moja kwa nne jumlisha mbili kwa nne. Swali namba kumi na mbili. Moja kwa kumi na tano jumlisha sita kwa kumi na tano.",
            "pg099_n0008": "Swali namba kumi na tatu. Tatu kwa tisa jumlisha nne kwa tisa. Swali namba kumi na nne. Tatu kwa saba jumlisha tatu kwa saba. Swali namba kumi na tano. Sifuri kwa tano jumlisha mbili kwa tano.",
            "pg099_n0011": "Swali namba kumi na sita. Moja kwa tatu jumlisha moja kwa tatu. Swali namba kumi na saba. Mbili kwa saba jumlisha nne kwa saba. Swali namba kumi na nane. Kumi na moja kwa ishirini jumlisha saba kwa ishirini.",
            "pg099_n0014": "Swali namba kumi na tisa. Moja kwa kumi jumlisha tatu kwa kumi. Swali namba ishirini. Kumi na sita kwa thelathini na tano jumlisha tisa kwa thelathini na tano.",
            "pg099_n0016": "Mafumbo yenye dhana ya kujumlisha sehemu.",
            "pg099_n0017": "Mfano",
            "pg099_n0019": "Yona alijaza maji sehemu tatu kwa tisa ya pipa. Halima alijaza sehemu mbili kwa tisa ya pipa hilo. Je, wote wawili walijaza sehemu gani ya pipa?",
            "pg099_n0021": "Swali la mfano linahitaji kujumlisha sehemu zenye asili tisa.",
            "pg099_n0022": "Njia.",
            "pg099_n0024": "Yona alijaza tatu kwa tisa ya pipa.",
            "pg099_n0027": "Halima alijaza mbili kwa tisa ya pipa.",
            "pg099_n0030": "Jumlisha kiasi: tatu jumlisha mbili, sawa sawa na tano. Asili inabaki tisa.",
            "pg099_n0033": "Kwa hiyo, wote wawili walijaza sehemu tano kwa tisa ya pipa.",
        },
    },
    100: {
        "rate": 0.85,
        "remove": {"pg100_n0004", "pg100_n0005", "pg100_n0006", "pg100_n0008", "pg100_n0009", "pg100_n0011", "pg100_n0012", "pg100_n0013", "pg100_n0014", "pg100_n0015", "pg100_n0016", "pg100_n0018", "pg100_n0019", "pg100_n0021", "pg100_n0022", "pg100_n0023", "pg100_n0024", "pg100_n0026", "pg100_n0027", "pg100_n0029", "pg100_n0030", "pg100_n0031", "pg100_n0033", "pg100_n0034", "pg100_n0035", "pg100_n0036"},
        "replace": {
            "pg100_n0001": "Zoezi la Nne",
            "pg100_n0002": "Jibu maswali yafuatayo.",
            "pg100_n0003": "Swali namba moja. Mama alimpa mwanawe robo moja ya biskuti. Baadaye alimpa robo tatu ya biskuti hiyo. Jumla alimpatia sehemu gani ya biskuti hiyo?",
            "pg100_n0007": "Swali namba mbili. Masanja alikula moja kwa sita ya mkate, na Amani alikula mbili kwa sita ya mkate huo. Je, wote wawili walikula sehemu gani ya mkate?",
            "pg100_n0010": "Swali namba tatu. Mkulima aligawanya shamba lake katika sehemu nane. Alipanda mahindi katika nne kwa nane ya shamba, na maharage katika tatu kwa nane. Je, sehemu gani ya shamba ilipandwa mahindi na maharage?",
            "pg100_n0017": "Swali namba nne. Wanakijiji waliuza mbili kwa tano ya pamba kwenye chama cha ushirika cha Mlole, na tatu kwa tano kwenye chama cha ushirika cha Mwadui. Waliuza sehemu gani ya pamba yote?",
            "pg100_n0025": "Swali namba tano. Tausi alitumia moja kwa saba ya mshahara wake kulipia kodi ya pango, na tatu kwa saba kwa chakula. Je, alitumia sehemu gani ya mshahara wake kwa kodi na chakula?",
            "pg100_n0032": "Swali namba sita. Maunda alinunua samaki wawili. Mmoja alikuwa na uzito wa mbili kwa nne ya kilogramu, na mwingine mbili kwa nne ya kilogramu. Tafuta jumla ya uzito wa samaki hao.",
        },
    },
    101: {
        "rate": 0.85,
        "remove": {"pg101_n0002", "pg101_n0003", "pg101_n0004", "pg101_n0005", "pg101_n0006", "pg101_n0007", "pg101_n0008", "pg101_n0009", "pg101_n0011", "pg101_n0012", "pg101_n0013", "pg101_n0014", "pg101_n0016", "pg101_n0017", "pg101_n0018", "pg101_n0019", "pg101_n0020", "pg101_n0021", "pg101_n0023", "pg101_n0024", "pg101_n0028", "pg101_n0031", "pg101_n0032", "pg101_n0033"},
        "replace": {
            "pg101_n0001": "Swali namba saba. Wakazi wa kijiji cha Maendeleo walitaka kujenga kituo cha afya. Wanakijiji walifyatua tano kwa kumi ya matofali yaliyohitajika, na tatu kwa kumi yalitolewa na mwenyekiti wa kijiji. Kijiji kina sehemu gani ya matofali yote yanayohitajika?",
            "pg101_n0010": "Swali namba nane. Nuru aliuza tatu kwa kumi ya machungwa siku ya kwanza, na sita kwa kumi siku ya pili. Kwa siku mbili aliuza sehemu gani ya machungwa yote?",
            "pg101_n0015": "Swali namba tisa. Shule ilinunua vitabu. Nne kwa kumi na mbili vilikuwa vya Hisabati, mbili kwa kumi na mbili vya Kiswahili, na tatu kwa kumi na mbili vya Sayansi na Teknolojia. Vitabu vya masomo hayo matatu ni sehemu gani ya vitabu vyote?",
            "pg101_n0022": "Swali namba kumi. Chora michoro na weka kivuli kuonesha: tatu kwa saba jumlisha mbili kwa saba, sawa sawa na tano kwa saba.",
            "pg101_n0026": "Kutoa sehemu zenye asili moja.",
            "pg101_n0027": "Unaweza kutoa sehemu zenye asili moja kwa kutumia michoro, mstari wa namba au namba pekee.",
            "pg101_n0029": "Mfano wa Kwanza",
            "pg101_n0030": "Kwa kutumia michoro, tafuta jibu sahihi. Tatu kwa tatu kutoa moja kwa tatu, sawa sawa na ngapi?",
            "pg101_n0034": "Hatua.",
            "pg101_n0035": "Hatua ya kwanza. Chora duara moja.",
        },
    },
    102: {
        "rate": 0.85,
        "remove": {"pg102_n0002", "pg102_n0006", "pg102_n0009", "pg102_n0010", "pg102_n0011", "pg102_n0013", "pg102_n0014", "pg102_n0015", "pg102_n0016", "pg102_n0018", "pg102_n0021", "pg102_n0022", "pg102_n0023"},
        "replace": {
            "pg102_n0001": "Hatua ya pili. Gawanya duara katika vipande vitatu vilivyo sawa, kisha andika sehemu tatu kwa tatu.",
            "pg102_n0003": "Hatua ya tatu. Weka kivuli kwenye kipande kimoja kati ya vitatu.",
            "pg102_n0004": "Hatua ya nne. Andika sehemu iliyotiwa kivuli: moja kwa tatu.",
            "pg102_n0005": "Hatua ya tano. Ondoa kipande kimoja ulichoweka kivuli kwenye duara.",
            "pg102_n0007": "Hatua ya sita. Chora tena kuonesha sehemu ya duara iliyobaki.",
            "pg102_n0008": "Hatua ya saba. Andika sehemu iliyobaki: mbili kwa tatu.",
            "pg102_n0012": "Sehemu moja kati ya tatu iliyowekwa kivuli imeondolewa.",
            "pg102_n0017": "Kwa hiyo, tatu kwa tatu kutoa moja kwa tatu, sawa sawa na mbili kwa tatu.",
            "pg102_n0019": "Mfano wa Pili",
            "pg102_n0020": "Kwa kutumia mstari wa namba, tafuta jibu sahihi. Nne kwa sita kutoa tatu kwa sita, sawa sawa na ngapi?",
            "pg102_n0024": "Hatua.",
            "pg102_n0025": "Hatua ya kwanza. Chora mstari.",
            "pg102_n0026": "Hatua ya pili. Gawanya mstari katika vipande sita vinavyolingana.",
        },
    },
    103: {
        "rate": 0.85,
        "remove": {"pg103_n0001", "pg103_n0003", "pg103_n0004", "pg103_n0006", "pg103_n0007", "pg103_n0009", "pg103_n0013", "pg103_n0015", "pg103_n0016", "pg103_n0017", "pg103_n0018", "pg103_n0019", "pg103_n0021", "pg103_n0024", "pg103_n0025", "pg103_n0026", "pg103_n0029", "pg103_n0031", "pg103_n0032", "pg103_n0033", "pg103_n0035"},
        "replace": {
            "pg103_n0002": "Maelezo ya mchoro wa mstari wa namba. Mstari unaanzia sifuri na umegawanywa katika sehemu sita sawa, kuanzia moja kwa sita hadi sita kwa sita. Hatua ya tatu. Ukianzia sifuri, alama ya kwanza kulia ni moja kwa sita.",
            "pg103_n0005": "Endelea kuweka alama mbili kwa sita, tatu kwa sita, nne kwa sita, tano kwa sita, hadi sita kwa sita.",
            "pg103_n0008": "Mwisho wa mstari ni sita kwa sita.",
            "pg103_n0010": "Hatua ya nne. Anzia sifuri, nenda hatua nne kulia hadi nne kwa sita.",
            "pg103_n0011": "Hatua ya tano. Kutoka nne kwa sita, rudi nyuma hatua tatu.",
            "pg103_n0012": "Rudi kuelekea upande wa kushoto kwenye mstari wa namba.",
            "pg103_n0014": "Hatua ya sita. Soma sehemu ulipoishia. Ni moja kwa sita.",
            "pg103_n0020": "Kwa hiyo, nne kwa sita kutoa tatu kwa sita, sawa sawa na moja kwa sita.",
            "pg103_n0022": "Mfano wa Tatu",
            "pg103_n0023": "Tafuta jibu sahihi. Kumi na moja kwa kumi na mbili kutoa saba kwa kumi na mbili, sawa sawa na ngapi?",
            "pg103_n0027": "Hatua.",
            "pg103_n0028": "Hatua ya kwanza. Toa namba za kiasi kama unavyotoa namba za kawaida. Kumi na moja kutoa saba, sawa sawa na nne.",
            "pg103_n0030": "Hatua ya pili. Asili haibadiliki; inabaki kumi na mbili.",
            "pg103_n0034": "Kwa hiyo, kumi na moja kwa kumi na mbili kutoa saba kwa kumi na mbili, sawa sawa na nne kwa kumi na mbili.",
        },
    },
    104: {
        "rate": 0.85,
        "remove": {"pg104_n0003", "pg104_n0005", "pg104_n0006", "pg104_n0008", "pg104_n0009", "pg104_n0011", "pg104_n0012", "pg104_n0014", "pg104_n0015", "pg104_n0017", "pg104_n0018", "pg104_n0020", "pg104_n0021", "pg104_n0023", "pg104_n0030", "pg104_n0032", "pg104_n0033", "pg104_n0035"},
        "replace": {
            "pg104_n0001": "Zoezi la Tano",
            "pg104_n0002": "Jibu maswali yafuatayo.",
            "pg104_n0004": "Swali namba moja. Tano kwa nane kutoa tatu kwa nane. Swali namba mbili. Mbili kwa tano kutoa moja kwa tano. Swali namba tatu. Nne kwa tisa kutoa moja kwa tisa.",
            "pg104_n0007": "Swali namba nne. Sita kwa saba kutoa nne kwa saba. Swali namba tano. Mbili kwa tatu kutoa moja kwa tatu. Swali namba sita. Tatu kwa tatu kutoa moja kwa tatu.",
            "pg104_n0010": "Swali namba saba. Tatu kwa sita kutoa moja kwa sita. Swali namba nane. Saba kwa nane kutoa tano kwa nane. Swali namba tisa. Sita kwa kumi na tatu kutoa tatu kwa kumi na tatu.",
            "pg104_n0013": "Swali namba kumi. Tatu kwa tano kutoa mbili kwa tano. Swali namba kumi na moja. Nne kwa tano kutoa moja kwa tano. Swali namba kumi na mbili. Tano kwa saba kutoa tatu kwa saba.",
            "pg104_n0016": "Swali namba kumi na tatu. Mbili kwa sita kutoa mbili kwa sita. Swali namba kumi na nne. Mbili kwa mbili kutoa moja kwa mbili. Swali namba kumi na tano. Tano kwa kumi kutoa moja kwa kumi.",
            "pg104_n0019": "Swali namba kumi na sita. Nne kwa nne kutoa mbili kwa nne. Swali namba kumi na saba. Tano kwa kumi na moja kutoa moja kwa kumi na moja. Swali namba kumi na nane. Kumi na sita kwa hamsini kutoa tano kwa hamsini.",
            "pg104_n0022": "Swali namba kumi na tisa. Ishirini na nne kwa ishirini na tano kutoa ishirini kwa ishirini na tano. Swali namba ishirini. Sabini na tano kwa mia moja kutoa hamsini kwa mia moja.",
            "pg104_n0024": "Mafumbo yenye dhana ya kutoa sehemu.",
            "pg104_n0025": "Mfano",
            "pg104_n0026": "Tano kwa nane ya shamba imepandwa miti ya mikaratusi. Sehemu iliyobaki imepandwa miti ya michungwa. Sehemu gani ya shamba imepandwa miti ya michungwa?",
            "pg104_n0029": "Hatua.",
            "pg104_n0031": "Hatua ya kwanza. Shamba lote limegawanywa katika vipande nane; shamba lote ni nane kwa nane.",
            "pg104_n0034": "Hatua ya pili. Sehemu iliyopandwa miti ya mikaratusi ni tano kwa nane.",
        },
    },
    105: {
        "rate": 0.85,
        "remove": {"pg105_n0001", "pg105_n0003", "pg105_n0004", "pg105_n0005", "pg105_n0006", "pg105_n0008", "pg105_n0009", "pg105_n0010", "pg105_n0014", "pg105_n0016", "pg105_n0018", "pg105_n0019", "pg105_n0020", "pg105_n0021", "pg105_n0023", "pg105_n0024", "pg105_n0026", "pg105_n0028", "pg105_n0030", "pg105_n0031", "pg105_n0032"},
        "replace": {
            "pg105_n0002": "Hatua ya tatu. Sehemu ya michungwa ni shamba lote kutoa sehemu ya mikaratusi. Nane kwa nane kutoa tano kwa nane, sawa sawa na tatu kwa nane.",
            "pg105_n0007": "Kwa hiyo, sehemu ya shamba iliyopandwa miti ya michungwa ni tatu kwa nane.",
            "pg105_n0011": "Zoezi la Sita",
            "pg105_n0012": "Jibu maswali yafuatayo.",
            "pg105_n0013": "Swali namba moja. Nusu ya shamba la Ngosha limelimwa. Je, ni sehemu gani ya shamba haijalimwa?",
            "pg105_n0015": "Swali namba mbili. Aisha alivuna machungwa. Ikiwa robo ya machungwa hayo yaliharibika, ni sehemu gani hayakuharibika?",
            "pg105_n0017": "Swali namba tatu. Bahati alikata tikitimaji katika vipande kumi vinavyolingana. Iwapo saba kwa kumi ya tikitimaji iliuzwa, sehemu gani haikuuzwa?",
            "pg105_n0022": "Swali namba nne. Mariam alikula moja kwa sita ya muwa wote. Sehemu gani ya muwa ilibaki?",
            "pg105_n0025": "Swali namba tano. Kandi alikuwa na tano kwa tisa ya mkate. Akampatia Ali nne kwa tisa ya mkate huo. Je, alibakiwa na sehemu gani?",
            "pg105_n0029": "Swali namba sita. Kabula alifanya saba kwa kumi na mbili ya maswali ya Hisabati asubuhi, na mbili kwa kumi na mbili mchana. Sehemu gani ya maswali ilibaki?",
        },
    },
    106: {
        "rate": 0.85,
        "remove": {"pg106_n0001", "pg106_n0003", "pg106_n0005", "pg106_n0006", "pg106_n0007", "pg106_n0009", "pg106_n0010", "pg106_n0011", "pg106_n0012", "pg106_n0014", "pg106_n0015", "pg106_n0018", "pg106_n0020"},
        "replace": {
            "pg106_n0002": "Swali namba saba. Chora michoro kuonesha: nne kwa tano kutoa moja kwa tano, sawa sawa na tatu kwa tano.",
            "pg106_n0004": "Swali namba nane. Robo tatu ya shamba la Kwame inapakana na barabara kuu. Sehemu gani ya shamba haipakani na barabara kuu?",
            "pg106_n0008": "Swali namba tisa. Bakari alitumia moja kwa kumi ya mshahara wake kulipa kodi, na mbili kwa kumi kulipa bili ya maji na umeme. Alibakiwa na sehemu gani ya mshahara?",
            "pg106_n0013": "Swali namba kumi. Wanakijiji walipanda miche ya miti ya matunda. Iwapo mbili kwa saba ya miti yote ilikauka, sehemu gani ya miti ilistawi?",
            "pg106_n0016": "Jikumbushe",
            "pg106_n0017": "Jambo la kwanza. Namba iliyo juu ya mstari wa sehemu huitwa kiasi; iliyo chini huitwa asili.",
            "pg106_n0019": "Jambo la pili. Unapojumlisha au kutoa sehemu zenye asili moja, asili haibadiliki.",
        },
    },
    107: {
        "rate": 0.85,
        "remove": {"pg107_n0005", "pg107_n0006", "pg107_n0007", "pg107_n0008", "pg107_n0009", "pg107_n0010", "pg107_n0013", "pg107_n0014", "pg107_n0017", "pg107_n0018", "pg107_n0019", "pg107_n0020"},
        "replace": {
            "pg107_n0001": "Sura ya Tisa",
            "pg107_n0002": "Wakati",
            "pg107_n0003": "Utangulizi",
            "pg107_n0004": "Wakati ni muhimu sana katika maisha ya kila siku. Wakati hupimwa kwa kutumia vipimo rasmi na visivyo rasmi. Katika sura hii, utajifunza kusoma, kuandika, kujumlisha na kutoa muda katika saa na dakika. Pia utajifunza kufumbua mafumbo yenye dhana ya wakati. Ujuzi huu utakusaidia kutumia wakati katika ujifunzaji, ufundishaji, biashara, kilimo na burudani.",
            "pg107_n0011": "Vipimo vya wakati",
            "pg107_n0012": "Vipimo vya wakati vimegawanyika katika makundi mawili: vipimo visivyo rasmi na vipimo rasmi.",
            "pg107_n0015": "Vipimo vya wakati visivyo rasmi",
            "pg107_n0016": "Unaweza kupima wakati kwa kutumia vitu katika mazingira. Kwa mfano, kuwika kwa jogoo au kivuli cha jua. Jogoo akiwika alfajiri, unajua asubuhi inakaribia. Kivuli huwa kirefu asubuhi, kifupi mchana na kirefu jioni.",
        },
    },
    108: {
        "rate": 0.85,
        "remove": {"pg108_n0003", "pg108_n0010", "pg108_n0011", "pg108_n0014", "pg108_n0015", "pg108_n0016", "pg108_n0017"},
        "replace": {
            "pg108_n0001": "Kazi namba moja",
            "pg108_n0002": "Chunguza picha zifuatazo kisha jibu maswali. Maelezo ya picha: picha a ina jua lililo chini angani na mti wenye kivuli kirefu kinachoelekea upande mmoja. Picha b ina jua lililo juu angani na mti wenye kivuli kifupi karibu na shina.",
            "pg108_n0004": "Maswali.",
            "pg108_n0005": "Swali namba moja. Ni picha ipi inaonesha wakati wa asubuhi au jioni?",
            "pg108_n0006": "Swali namba mbili. Ni picha gani inaonesha wakati wa mchana?",
            "pg108_n0007": "Swali namba tatu. Unawezaje kutambua wakati bila kutumia jua?",
            "pg108_n0008": "Vipimo rasmi vya wakati",
            "pg108_n0009": "Unaweza kupima wakati kwa usahihi kwa kutumia saa, siku, wiki, mwezi, mwaka, muongo na karne. Saa moja ina dakika sitini. Dakika moja ina sekunde sitini. Siku moja ina saa ishirini na nne.",
            "pg108_n0012": "Kusoma saa katika mtindo wa saa kumi na mbili.",
            "pg108_n0013": "Katika saa ya mshale, mshale mfupi mnene huonesha saa. Mshale mrefu mnene huonesha dakika. Mshale mrefu zaidi na mwembamba huonesha sekunde. Katika saa ya kidijitali, saa na dakika hutenganishwa kwa nukta mbili. Muda huoneshwa kwa namba za Kiarabu au namba za Kirumi.",
        },
    },
    109: {
        "rate": 0.85,
        "remove": {"pg109_n0003", "pg109_n0012", "pg109_n0013", "pg109_n0014", "pg109_n0015", "pg109_n0016", "pg109_n0017", "pg109_n0018", "pg109_n0019", "pg109_n0020"},
        "replace": {
            "pg109_n0001": "Kazi namba mbili",
            "pg109_n0002": "Chunguza nyuso za saa a, b na c, kisha jibu maswali. Uso a ni saa ya mshale yenye namba za Kiarabu; mshale wa dakika unaelekea kumi na mbili na mshale wa saa unaelekea tatu. Uso b ni saa ya mshale yenye namba za Kirumi; mshale wa dakika unaelekea sita na mshale wa saa uko kati ya saba na nane. Uso c ni saa ya kidijitali inayoonesha tarakimu sifuri tatu, nukta mbili, sifuri sifuri.",
            "pg109_n0004": "Maswali.",
            "pg109_n0005": "Swali namba moja. Uso wa saa a ni saa ya aina gani?",
            "pg109_n0006": "Swali namba mbili. Uso wa saa b unaonesha muda gani?",
            "pg109_n0007": "Swali namba tatu. Uso wa saa a unaonesha muda gani?",
            "pg109_n0008": "Swali namba nne. Uso wa saa c unaonesha muda gani?",
            "pg109_n0009": "Swali namba tano. Kuna tofauti gani kati ya uso wa saa a na uso wa saa b?",
            "pg109_n0010": "Kazi namba tatu",
            "pg109_n0011": "Sehemu a. Chunguza mchoro uliooneshwa kisha jibu maswali yanayofuata. Sauti haisuluhishi mchoro huu kwa niaba ya mwanafunzi.",
        },
    },
    110: {
        "rate": 0.85,
        "remove": {"pg110_n0006", "pg110_n0007", "pg110_n0008", "pg110_n0009", "pg110_n0010", "pg110_n0011"},
        "replace": {
            "pg110_n0001": "Maswali ya sehemu a.",
            "pg110_n0002": "Jaza nafasi zilizoachwa wazi.",
            "pg110_n0003": "Swali namba moja. Sekunde sitini ni sawa na dashi moja.",
            "pg110_n0004": "Swali namba mbili. Saa moja ina dakika ngapi?",
            "pg110_n0005": "Sehemu b. Chunguza mchoro unaooneshwa kisha jibu maswali.",
            "pg110_n0012": "Muda pia hupimwa kwa siku, wiki, mwezi au mwaka.",
            "pg110_n0013": "Namba ya Kirumi I. Siku moja ina saa ishirini na nne.",
            "pg110_n0014": "Namba ya Kirumi II. Wiki moja ina siku saba.",
            "pg110_n0015": "Namba ya Kirumi III. Mwezi mmoja una siku kati ya ishirini na nane na thelathini na moja.",
            "pg110_n0016": "Namba ya Kirumi IV. Mwaka mmoja una miezi kumi na miwili.",
            "pg110_n0017": "Maswali ya sehemu b.",
            "pg110_n0018": "Jaza nafasi zilizoachwa wazi.",
            "pg110_n0019": "Swali namba moja. Saa ishirini na nne ni sawa na siku ngapi?",
            "pg110_n0020": "Swali namba mbili. Siku saba ni sawa na wiki ngapi?",
            "pg110_n0021": "Swali namba tatu. Miezi kumi na miwili ni sawa na nini kimoja?",
        },
    },
    111: {
        "rate": 0.85,
        "remove": {
            "pg111_n0011", "pg111_n0012", "pg111_n0013", "pg111_n0014",
            "pg111_n0015", "pg111_n0016", "pg111_n0017", "pg111_n0018", "pg111_n0019",
        },
        "replace": {
            "pg111_n0004": "Jedwali la majina ya siku katika wiki.",
            "pg111_n0005": "Tukisoma kutoka kushoto kwenda kulia: Jumatatu, Jumanne, Jumatano, Alhamisi, Ijumaa, Jumamosi na Jumapili.",
            "pg111_n0009": "Jedwali la majina ya miezi na idadi ya siku. Tunasoma kila mwezi pamoja na namba yake na idadi ya siku.",
            "pg111_n0010": "Januari ni mwezi wa kwanza, una siku thelathini na moja. Februari ni mwezi wa pili, una siku ishirini na nane au ishirini na tisa. Machi ni mwezi wa tatu, una siku thelathini na moja. Aprili ni mwezi wa nne, una siku thelathini. Mei ni mwezi wa tano, una siku thelathini na moja. Juni ni mwezi wa sita, una siku thelathini. Julai ni mwezi wa saba, una siku thelathini na moja. Agosti ni mwezi wa nane, una siku thelathini na moja. Septemba ni mwezi wa tisa, una siku thelathini. Oktoba ni mwezi wa kumi, una siku thelathini na moja. Novemba ni mwezi wa kumi na moja, una siku thelathini. Desemba ni mwezi wa kumi na mbili, una siku thelathini na moja.",
            "pg111_n0020": "Muda katika miaka hupimwa kwa muongo au karne.",
            "pg111_n0021": "Sehemu a. Muongo mmoja una miaka kumi.",
            "pg111_n0022": "Sehemu b. Karne moja ina miaka mia moja.",
        },
    },
    112: {
        "rate": 0.85,
        "remove": {"pg112_n0003", "pg112_n0004", "pg112_n0014", "pg112_n0016", "pg112_n0017", "pg112_n0019", "pg112_n0020"},
        "replace": {
            "pg112_n0001": "Nyakati katika siku",
            "pg112_n0002": "Nyakati katika siku zinatofautiana kulingana na muda. Jedwali lina safu mbili: wakati na muda.",
            "pg112_n0005": "Mstari wa kwanza. Alfajiri: saa kumi na moja hadi saa kumi na mbili alfajiri.",
            "pg112_n0006": "Mstari wa pili. Asubuhi: saa moja hadi saa tano asubuhi.",
            "pg112_n0007": "Mstari wa tatu. Adhuhuri: saa sita kamili adhuhuri.",
            "pg112_n0008": "Mstari wa nne. Mchana: saa sita hadi saa nane mchana.",
            "pg112_n0009": "Mstari wa tano. Alasiri: saa tisa kamili alasiri.",
            "pg112_n0010": "Mstari wa sita. Jioni: saa kumi hadi saa kumi na mbili jioni.",
            "pg112_n0011": "Mstari wa saba. Usiku: saa moja hadi saa kumi usiku.",
            "pg112_n0012": "Majira ya mwaka",
            "pg112_n0013": "Majira ya mwaka ni vipindi tofauti: masika na kiangazi.",
            "pg112_n0015": "Maelezo ya picha. Picha a, masika: mvua inanyesha, mazingira yana majani mabichi na mti wenye majani mengi. Picha b, kiangazi: jua linawaka, ardhi ni kavu na mti hauna majani.",
            "pg112_n0018": "Majira ya masika huwa na mvua nyingi ambazo zinaweza kusababisha mafuriko. Pia ni wakati wa shughuli mbalimbali za kilimo.",
        },
    },
    113: {
        "rate": 0.85,
        "remove": {"pg113_n0002", "pg113_n0003", "pg113_n0007", "pg113_n0008", "pg113_n0009", "pg113_n0010", "pg113_n0011", "pg113_n0012", "pg113_n0014", "pg113_n0015", "pg113_n0016", "pg113_n0017", "pg113_n0018", "pg113_n0020", "pg113_n0021", "pg113_n0028", "pg113_n0031"},
        "replace": {
            "pg113_n0001": "Majira ya kiangazi huwa hayana mvua. Mito mingi hupungua maji au hukauka. Baadhi ya mimea hukauka kwa kukosa maji. Huu ni wakati ambao baadhi ya mazao huvunwa mashambani.",
            "pg113_n0004": "Kazi namba nne",
            "pg113_n0005": "Soma hadithi ifuatayo kisha jibu maswali.",
            "pg113_n0006": "Maria na Rajabu wanaishi kijiji cha Luganga na wanasoma Shule ya Msingi Itamba. Kila siku hutembea saa mbili kuelekea shuleni. Huamka alfajiri ili kuwahi. Kabla ya kufika huvuka mto Itamba. Mto hujaa wakati wa masika, lakini maji hupungua wakati wa kiangazi.",
            "pg113_n0013": "Siku moja wakati wa masika, mvua ilinyesha kuanzia saa tatu asubuhi hadi saa sita mchana. Maria na Rajabu waliingiwa na hofu. Mwalimu alipowaruhusu kurudi nyumbani saa kumi jioni, waliogopa. Mwalimu aliamua kuwasindikiza.",
            "pg113_n0019": "Karibu na mto waliwakuta wanakijiji wakijenga daraja la miti. Walishirikiana nao. Ilipofika saa moja usiku, daraja lilikuwa limekamilika. Wote walifurahi.",
            "pg113_n0022": "Maswali.",
            "pg113_n0023": "Swali namba moja. Taja nyakati mbalimbali zilizopo kwenye hadithi.",
            "pg113_n0024": "Swali namba mbili. Maria na Rajabu huamka wakati gani?",
            "pg113_n0025": "Swali namba tatu. Mto Itamba hujaa maji wakati gani?",
            "pg113_n0026": "Swali namba nne. Ni wakati gani maji ya mto Itamba hupungua?",
            "pg113_n0027": "Swali namba tano. Mvua ilianza kunyesha wakati gani?",
            "pg113_n0029": "Swali namba sita. Mvua hiyo iliisha wakati gani?",
            "pg113_n0030": "Swali namba saba. Wanafunzi wa Shule ya Msingi Itamba huruhusiwa kurudi nyumbani wakati gani?",
        },
    },
    114: {
        "rate": 0.85,
        "remove": {"pg114_n0022", "pg114_n0023", "pg114_n0024", "pg114_n0025"},
        "replace": {
            "pg114_n0001": "Swali namba nane. Daraja lilikamilika kujengwa wakati gani?",
            "pg114_n0002": "Swali namba tisa. Ni majira gani mvua hunyesha kwa wingi?",
            "pg114_n0003": "Swali namba kumi. Ni majira gani mvua hainyeshi?",
            "pg114_n0004": "Zoezi la Kwanza",
            "pg114_n0005": "Jibu maswali yafuatayo.",
            "pg114_n0006": "Swali namba moja. Ali alitembea kutoka darasani hadi ofisi ya walimu kwa sekunde sitini. Sekunde hizo ni sawa na dakika ngapi?",
            "pg114_n0008": "Swali namba mbili. Wanafunzi walipewa jaribio la Hisabati la dakika sitini. Dakika hizo ni sawa na saa ngapi?",
            "pg114_n0010": "Swali namba tatu. Juma alisafiri kutoka Dar es Salaam hadi Kibaha kwa saa moja. Alitumia dakika ngapi?",
            "pg114_n0012": "Swali namba nne. John alinunua muda wa maongezi uliodumu saa ishirini na nne. Saa hizo ni sawa na siku ngapi?",
            "pg114_n0014": "Swali namba tano. Mwezi wa kumi na mbili shule hufungwa kwa likizo. Andika jina la mwezi huo.",
            "pg114_n0016": "Swali namba sita. Kikao cha wazazi kilianza alasiri. Hii ni sawa na saa ngapi?",
            "pg114_n0018": "Swali namba saba. Muongo mmoja ni sawa na miaka mingapi?",
            "pg114_n0019": "Swali namba nane. Muda wa miaka mia moja unaitwaje?",
            "pg114_n0020": "Swali namba tisa. Jaza nafasi zilizoachwa wazi katika jedwali lifuatalo.",
            "pg114_n0021": "Jedwali lina safu saba. Safu ya kwanza: siku tatu ni sawa na saa ngapi? Safu ya pili: wiki mbili ni sawa na siku ngapi? Safu ya tatu: saa tatu ni sawa na dakika ngapi? Safu ya nne: miaka miwili ni sawa na miezi mingapi? Safu ya tano: mwaka mmoja ni sawa na miezi mingapi? Safu ya sita: miaka miwili mifupi ni sawa na siku ngapi? Safu ya saba: karne moja ni sawa na miaka mingapi?",
            "pg114_n0026": "Swali namba kumi. Mwezi Februari una siku ngapi katika mwaka mrefu?",
        },
    },
    115: {
        "rate": 0.85,
        "remove": {"pg115_n0004", "pg115_n0005", "pg115_n0006", "pg115_n0007", "pg115_n0008", "pg115_n0009", "pg115_n0011", "pg115_n0012", "pg115_n0013", "pg115_n0014", "pg115_n0015", "pg115_n0016", "pg115_n0017", "pg115_n0018", "pg115_n0019", "pg115_n0020", "pg115_n0021", "pg115_n0022", "pg115_n0023", "pg115_n0024", "pg115_n0025", "pg115_n0026", "pg115_n0027", "pg115_n0028"},
        "replace": {
            "pg115_n0001": "Uso wa saa",
            "pg115_n0002": "Uso wa saa una mishale mitatu inayoanzia katikati.",
            "pg115_n0003": "Mishale huonesha muda kwa namba za Kiarabu au Kirumi. Mshale mfupi huonesha saa, mshale mrefu mnene huonesha dakika, na mshale mrefu mwembamba huonesha sekunde.",
            "pg115_n0010": "Mishale yote huzunguka kuanzia kushoto kuelekea kulia. Mshale mfupi hutumia saa kumi na mbili kumaliza mzunguko mmoja. Mshale wa dakika hutumia dakika sitini. Mchoro wa uso wa saa umetolewa kwa uchunguzi; sauti haitafsiri nafasi za mishale kwa niaba ya mwanafunzi.",
            "pg115_n0029": "Saa moja ni sawa na dakika sitini. Pia, dakika sitini ni sawa na saa moja.",
        },
    },
    116: {
        "rate": 0.85,
        "remove": {"pg116_n0003", "pg116_n0004", "pg116_n0005", "pg116_n0006", "pg116_n0007", "pg116_n0008", "pg116_n0009", "pg116_n0010", "pg116_n0011", "pg116_n0012", "pg116_n0013", "pg116_n0014", "pg116_n0015", "pg116_n0016", "pg116_n0017", "pg116_n0018", "pg116_n0019", "pg116_n0020", "pg116_n0026", "pg116_n0028", "pg116_n0031", "pg116_n0032", "pg116_n0033", "pg116_n0034", "pg116_n0035", "pg116_n0036", "pg116_n0037", "pg116_n0039"},
        "replace": {
            "pg116_n0001": "Nusu saa.",
            "pg116_n0002": "Robo saa.",
            "pg116_n0021": "Dakika thelathini ni nusu saa. Dakika kumi na tano ni robo saa.",
            "pg116_n0022": "Kazi namba tano",
            "pg116_n0023": "Kuchora uso wa saa.",
            "pg116_n0024": "Hatua.",
            "pg116_n0025": "Hatua ya kwanza. Andaa kitu cha duara kama sarafu ya shilingi mia mbili, shilingi mia tano, au mfuniko wa chupa.",
            "pg116_n0027": "Hatua ya pili. Weka kitu kwenye karatasi, kisha tumia penseli kuchora duara kwa kuzungushia kitu.",
            "pg116_n0029": "Hatua ya tatu. Weka alama kumi na mbili kwa nafasi zinazolingana kama zilivyo kwenye mchoro.",
            "pg116_n0038": "Hatua ya nne. Andika namba moja hadi kumi na mbili kwenye alama ulizoweka.",
        },
    },
    117: {
        "rate": 0.85,
        "remove": {"pg117_n0007", "pg117_n0009", "pg117_n0010", "pg117_n0011", "pg117_n0013", "pg117_n0014", "pg117_n0016"},
        "replace": {
            "pg117_n0001": "Hatua ya tano. Chora mshale mfupi mnene kutoka katikati ukilenga namba nne.",
            "pg117_n0002": "Hatua ya sita. Chora mshale mrefu mnene kutoka katikati ukilenga namba kumi na mbili.",
            "pg117_n0003": "Hatua ya saba. Uso wa saa unaonesha saa ngapi?",
            "pg117_n0004": "Kusoma muda kwa kutumia saa.",
            "pg117_n0005": "Mfano",
            "pg117_n0006": "Soma muda katika saa zifuatazo.",
            "pg117_n0008": "Saa ya kwanza: saa kumi na mbili kamili, huandikwa kumi na mbili nukta mbili sifuri sifuri. Saa ya pili: saa nne kamili, huandikwa nne nukta mbili sifuri sifuri. Saa ya tatu: saa tisa kamili, huandikwa tisa nukta mbili sifuri sifuri.",
            "pg117_n0012": "Saa ya nne: saa moja na dakika thelathini. Saa ya tano: saa nane na dakika thelathini. Saa ya sita: saa sita na dakika thelathini.",
            "pg117_n0015": "Saa ya saba: saa tano na dakika kumi na tano. Saa ya nane: saa mbili na dakika kumi na tano. Saa ya tisa: saa kumi na moja na dakika kumi na tano.",
        },
    },
    118: {
        "rate": 0.85,
        "remove": {"pg118_n0010", "pg118_n0011", "pg118_n0012", "pg118_n0013", "pg118_n0014", "pg118_n0015", "pg118_n0016", "pg118_n0018", "pg118_n0019", "pg118_n0020"},
        "replace": {
            "pg118_n0001": "Kuandika muda katika saa na dakika.",
            "pg118_n0002": "Mfano",
            "pg118_n0003": "Unapoandika muda, anza kuandika saa, halafu dakika.",
            "pg118_n0004": "Mfano wa kwanza. Saa sita kamili huandikwa sita nukta mbili sifuri sifuri.",
            "pg118_n0005": "Mfano wa pili. Saa kumi na mbili na dakika thelathini huandikwa kumi na mbili nukta mbili thelathini.",
            "pg118_n0006": "Mfano wa tatu. Saa kumi na dakika kumi na tano huandikwa kumi nukta mbili kumi na tano.",
            "pg118_n0007": "Zoezi la Pili",
            "pg118_n0008": "Jibu maswali yafuatayo.",
            "pg118_n0009": "Swali namba moja. Soma saa zifuatazo, kisha andika muda kwa namba na kwa maneno. Sehemu a: mshale wa dakika unaelekea tatu, na mshale wa saa uko karibu na tano. Sehemu b: mshale wa dakika unaelekea sita, na mshale wa saa uko kati ya moja na mbili. Sehemu c: mshale wa dakika unaelekea kumi na mbili, na mshale wa saa unaelekea sita. Sehemu d: saa ya kidijitali inaonesha sifuri nane, nukta mbili, arobaini na tano.",
            "pg118_n0017": "Swali namba mbili. Chora mishale kwenye nyuso za saa kuonesha muda uliotajwa. Sehemu a, saa tatu kamili. Sehemu b, saa nane na dakika thelathini.",
        },
    },
    119: {
        "rate": 0.85,
        "remove": {"pg119_n0001", "pg119_n0004", "pg119_n0013", "pg119_n0014", "pg119_n0015", "pg119_n0018"},
        "replace": {
            "pg119_n0002": "Muendelezo wa swali namba mbili. Sehemu c, chora saa sita kamili. Sehemu d, chora saa tisa na dakika kumi na tano.",
            "pg119_n0003": "Swali namba tatu. Jaza nafasi zilizoachwa wazi kwa kuandika muda kwa maneno.",
            "pg119_n0005": "Sehemu a. Kumi na mbili nukta mbili kumi na tano. Andika kwa maneno.",
            "pg119_n0006": "Sehemu b. Kumi na moja nukta mbili thelathini. Andika kwa maneno.",
            "pg119_n0007": "Sehemu c. Nane nukta mbili kumi na tano. Andika kwa maneno.",
            "pg119_n0008": "Sehemu d. Tano nukta mbili sifuri sifuri. Andika kwa maneno.",
            "pg119_n0009": "Kujumlisha muda katika saa na dakika.",
            "pg119_n0010": "Kujumlisha muda bila kubadili.",
            "pg119_n0011": "Saa moja ni sawa na dakika sitini.",
            "pg119_n0012": "Mfano wa Kwanza. Mpangilio wa wima una saa mbili na dakika ishirini na tano, jumlisha saa tatu na dakika kumi na tano.",
            "pg119_n0016": "Hatua.",
            "pg119_n0017": "Hatua ya kwanza. Jumlisha dakika: ishirini na tano jumlisha kumi na tano, sawa sawa na arobaini. Andika arobaini katika nafasi ya dakika.",
            "pg119_n0019": "Hatua ya pili. Jumlisha saa: mbili jumlisha tatu, sawa sawa na tano. Andika tano katika nafasi ya saa.",
            "pg119_n0020": "Kwa hiyo, jibu ni saa tano na dakika arobaini.",
        },
    },
    120: {
        "rate": 0.85,
        "remove": {"pg120_n0002", "pg120_n0003", "pg120_n0004", "pg120_n0005", "pg120_n0009", "pg120_n0010", "pg120_n0012", "pg120_n0013", "pg120_n0015", "pg120_n0016", "pg120_n0018", "pg120_n0019"},
        "replace": {
            "pg120_n0001": "Mfano wa Pili. Mpangilio wa wima: saa nne na dakika thelathini, jumlisha saa tano na dakika ishirini na nane, sawa sawa na saa tisa na dakika hamsini na nane.",
            "pg120_n0006": "Zoezi la Tatu",
            "pg120_n0007": "Jibu kila swali likamilike kabla ya kuanza linalofuata.",
            "pg120_n0008": "Swali namba moja. Saa tatu na dakika kumi na tano, jumlisha saa nne na dakika ishirini na tano. Swali namba mbili. Saa mbili na dakika kumi na saba, jumlisha saa moja na dakika ishirini. Swali namba tatu. Saa saba na dakika ishirini, jumlisha saa tano na dakika thelathini na tano.",
            "pg120_n0011": "Swali namba nne. Saa tatu na dakika thelathini, jumlisha saa tatu na dakika kumi. Swali namba tano. Saa tano na dakika arobaini na tano, jumlisha saa nne na dakika kumi na nne. Swali namba sita. Saa tano na dakika sifuri, jumlisha saa mbili na dakika hamsini na tisa.",
            "pg120_n0014": "Swali namba saba. Saa saba na dakika ishirini, jumlisha saa moja na dakika thelathini na tano. Swali namba nane. Saa sita na dakika tisa, jumlisha saa moja na dakika ishirini na nane. Swali namba tisa. Saa tatu na dakika nane, jumlisha saa sita na dakika hamsini na moja.",
            "pg120_n0017": "Swali namba kumi. Saa moja na dakika ishirini na mbili, jumlisha saa tatu na dakika ishirini.",
        },
    },
    121: {
        "rate": 0.85,
        "remove": {"pg121_n0003", "pg121_n0004", "pg121_n0005", "pg121_n0008", "pg121_n0010", "pg121_n0011", "pg121_n0017", "pg121_n0018", "pg121_n0020", "pg121_n0021"},
        "replace": {
            "pg121_n0001": "Kujumlisha muda katika saa na dakika kwa kubadili.",
            "pg121_n0002": "Mfano. Saa tatu na dakika arobaini na tano, jumlisha saa nne na dakika thelathini na tano.",
            "pg121_n0006": "Hatua.",
            "pg121_n0007": "Hatua ya kwanza. Jumlisha dakika. Zikizidi sitini, badili dakika sitini kuwa saa moja, kisha andika dakika zilizobaki.",
            "pg121_n0009": "Hatua ya pili. Dakika arobaini na tano jumlisha dakika thelathini na tano, sawa sawa na dakika themanini. Dakika themanini ni saa moja na dakika ishirini. Andika ishirini katika nafasi ya dakika.",
            "pg121_n0012": "Hatua ya tatu. Jumlisha saa: moja iliyobebwa, jumlisha tatu, jumlisha nne, sawa sawa na nane. Andika nane katika nafasi ya saa.",
            "pg121_n0013": "Kwa hiyo, jibu ni saa nane na dakika ishirini.",
            "pg121_n0014": "Zoezi la Nne",
            "pg121_n0015": "Jibu maswali yafuatayo.",
            "pg121_n0016": "Swali namba moja. Saa saba na dakika ishirini na tano, jumlisha saa mbili na dakika hamsini na tano. Swali namba mbili. Saa moja na dakika thelathini na saba, jumlisha saa nne na dakika ishirini na nne. Swali namba tatu. Saa nne na dakika arobaini, jumlisha saa tatu na dakika hamsini.",
            "pg121_n0019": "Swali namba nne. Saa mbili na dakika kumi na mbili, jumlisha saa moja na dakika arobaini na tisa. Swali namba tano. Saa tisa na dakika tano, jumlisha saa moja na dakika hamsini na nane. Swali namba sita. Saa tano na dakika thelathini, jumlisha saa nne na dakika thelathini.",
        },
    },
    122: {
        "rate": 0.85,
        "remove": {"pg122_n0002", "pg122_n0003", "pg122_n0005", "pg122_n0006", "pg122_n0013", "pg122_n0014", "pg122_n0015", "pg122_n0016", "pg122_n0017", "pg122_n0018", "pg122_n0019", "pg122_n0020", "pg122_n0021", "pg122_n0022", "pg122_n0023", "pg122_n0024", "pg122_n0025", "pg122_n0026", "pg122_n0027", "pg122_n0028", "pg122_n0029", "pg122_n0030", "pg122_n0031"},
        "replace": {
            "pg122_n0001": "Swali namba saba. Saa nne na dakika moja, jumlisha saa mbili na dakika hamsini na tisa. Swali namba nane. Saa tatu na dakika kumi, jumlisha saa mbili na dakika hamsini na tano. Swali namba tisa. Saa mbili na dakika arobaini na tisa, jumlisha saa saba na dakika kumi na nane.",
            "pg122_n0004": "Swali namba kumi. Saa nane na dakika thelathini na saba, jumlisha saa moja na dakika thelathini.",
            "pg122_n0008": "Kutoa muda katika saa na dakika.",
            "pg122_n0009": "Kutoa muda bila kubadili.",
            "pg122_n0010": "Kutoa dakika chache kutoka dakika nyingi ni sawa na kutoa namba za kawaida.",
            "pg122_n0012": "Mfano wa Kwanza. Saa sita na dakika ishirini na tano, kutoa saa tano na dakika kumi na tano. Hatua ya kwanza: toa dakika. Ishirini na tano kutoa kumi na tano, sawa sawa na kumi. Hatua ya pili: toa saa. Sita kutoa tano, sawa sawa na moja. Jibu ni saa moja na dakika kumi. Mfano wa Pili. Saa nane na dakika thelathini na saba, kutoa saa tatu na dakika ishirini na mbili. Hatua ya kwanza: toa dakika. Thelathini na saba kutoa ishirini na mbili, sawa sawa na kumi na tano. Hatua ya pili: toa saa. Nane kutoa tatu, sawa sawa na tano. Jibu ni saa tano na dakika kumi na tano.",
        },
    },
    123: {
        "rate": 0.85,
        "remove": {"pg123_n0001", "pg123_n0005", "pg123_n0006", "pg123_n0008", "pg123_n0009", "pg123_n0011", "pg123_n0012", "pg123_n0014", "pg123_n0015", "pg123_n0020", "pg123_n0021", "pg123_n0022", "pg123_n0023"},
        "replace": {
            "pg123_n0002": "Zoezi la Tano",
            "pg123_n0003": "Jibu maswali yafuatayo.",
            "pg123_n0004": "Swali namba moja. Saa tatu na dakika arobaini, kutoa saa moja na dakika ishirini na tano. Swali namba mbili. Saa kumi na dakika kumi na saba, kutoa saa mbili na dakika kumi na nne. Swali namba tatu. Saa tano na dakika hamsini na tano, kutoa saa tatu na dakika ishirini na nane.",
            "pg123_n0007": "Swali namba nne. Saa kumi na mbili na dakika thelathini na mbili, kutoa saa nane na dakika kumi na tisa. Swali namba tano. Saa tisa na dakika arobaini na tano, kutoa saa sita na dakika ishirini na tano. Swali namba sita. Saa saba na dakika kumi na sita, kutoa saa nne na dakika tisa.",
            "pg123_n0010": "Swali namba saba. Saa nane na dakika kumi na tano, kutoa saa tano na dakika kumi na mbili. Swali namba nane. Saa kumi na moja na dakika ishirini na nne, kutoa saa tisa na dakika kumi na nane. Swali namba tisa. Saa saba na dakika thelathini, kutoa saa mbili na dakika kumi na tano.",
            "pg123_n0013": "Swali namba kumi. Saa kumi na dakika arobaini, kutoa saa tisa na dakika arobaini.",
            "pg123_n0016": "Kutoa muda katika saa na dakika kwa kubadili.",
            "pg123_n0017": "Mfano. Saa tatu na dakika kumi na tano, kutoa saa moja na dakika arobaini na tano.",
            "pg123_n0018": "Hatua.",
            "pg123_n0019": "Hatua ya kwanza. Dakika kumi na tano kutoa dakika arobaini na tano haitoshi. Chukua saa moja kutoka saa tatu, kisha ibadili kuwa dakika sitini.",
        },
    },
    124: {
        "rate": 0.85,
        "remove": {"pg124_n0001", "pg124_n0003", "pg124_n0005", "pg124_n0011", "pg124_n0012", "pg124_n0014", "pg124_n0015", "pg124_n0017", "pg124_n0018", "pg124_n0020", "pg124_n0021"},
        "replace": {
            "pg124_n0002": "Hatua ya pili. Jumlisha dakika sitini na dakika kumi na tano; unapata dakika sabini na tano. Toa dakika arobaini na tano. Sabini na tano kutoa arobaini na tano, sawa sawa na thelathini. Andika dakika thelathini.",
            "pg124_n0004": "Hatua ya tatu. Ulipochukua saa moja kutoka saa tatu, zilibaki saa mbili.",
            "pg124_n0006": "Hatua ya nne. Toa saa: mbili kutoa moja, sawa sawa na moja. Andika saa moja.",
            "pg124_n0007": "Kwa hiyo, jibu ni saa moja na dakika thelathini.",
            "pg124_n0008": "Zoezi la Sita",
            "pg124_n0009": "Jibu maswali yafuatayo.",
            "pg124_n0010": "Swali namba moja. Saa kumi na mbili na dakika tano, kutoa saa tisa na dakika hamsini na tano. Swali namba mbili. Saa kumi na dakika kumi na nne, kutoa saa nane na dakika arobaini na saba. Swali namba tatu. Saa tano na dakika ishirini, kutoa saa mbili na dakika ishirini na saba.",
            "pg124_n0013": "Swali namba nne. Saa tisa na dakika sifuri, kutoa saa sita na dakika hamsini. Swali namba tano. Saa tano na dakika thelathini, kutoa saa moja na dakika arobaini na tano. Swali namba sita. Saa saba na dakika sifuri, kutoa saa sita na dakika arobaini na tano.",
            "pg124_n0016": "Swali namba saba. Saa nane na dakika kumi na moja, kutoa saa tatu na dakika thelathini na tano. Swali namba nane. Saa kumi na dakika ishirini na mbili, kutoa saa saba na dakika hamsini.",
            "pg124_n0019": "Swali namba tisa. Leo ni siku ya kwanza kwa Doto kuwa kwenye kambi ya skauti. Ratiba yake inaonekana katika jedwali la ukurasa unaofuata.",
        },
    },
    125: {
        "rate": 0.85,
        "replace": {
            "pg125_n0001": "Jedwali lina safu tatu: muda wa kuanza, muda wa kumaliza, na shughuli. Tunasoma mstari mmoja hadi ukamilike kabla ya kuendelea.",
            "pg125_n0002": "Mstari wa kwanza. Kuanzia saa moja asubuhi hadi saa mbili asubuhi: chai ya asubuhi.",
            "pg125_n0003": "Mstari wa pili. Kuanzia saa mbili asubuhi hadi saa tatu asubuhi: mazoezi ya viungo.",
            "pg125_n0004": "Mstari wa tatu. Kuanzia saa tatu asubuhi hadi saa nne na dakika arobaini na tano asubuhi: masomo ya nadharia.",
            "pg125_n0005": "Mstari wa nne. Kuanzia saa nne na dakika arobaini na tano asubuhi hadi saa sita na dakika kumi na tano mchana: mafunzo kwa vitendo.",
            "pg125_n0006": "Mstari wa tano. Kuanzia saa sita na dakika kumi na tano mchana hadi saa saba na dakika arobaini na tano mchana: chakula cha mchana.",
            "pg125_n0007": "Mstari wa sita. Kuanzia saa saba na dakika arobaini na tano mchana hadi saa kumi na dakika kumi na tano jioni: mafunzo ya vipimo.",
            "pg125_n0008": "Mstari wa saba. Kuanzia saa kumi na dakika kumi na tano jioni hadi saa kumi na mbili jioni: burudani.",
            "pg125_n0009": "Maswali ya swali namba tisa.",
            "pg125_n0010": "Sehemu a. Doto hutumia muda gani kula chakula cha mchana?",
            "pg125_n0011": "Sehemu b. Mafunzo kwa vitendo hutumia muda gani?",
            "pg125_n0012": "Sehemu c. Doto atakuwa anafanya nini saa tisa na dakika arobaini na tano alasiri?",
            "pg125_n0013": "Sehemu d. Doto alikuwa anafanya nini saa mbili na dakika ishirini na tano asubuhi?",
            "pg125_n0014": "Sehemu e. Shughuli zipi zinachukua zaidi ya saa moja na dakika thelathini?",
            "pg125_n0015": "Sehemu f. Doto atakuwa anafanya nini saa kumi na moja na dakika thelathini jioni?",
            "pg125_n0016": "Swali namba kumi. Kwa kutumia michoro ya saa ifuatayo, jaza muda uliotumika katika nafasi iliyo wazi.",
            "pg125_n0018": "Sehemu a. Saa ya kuanzia inaonesha saa kumi na moja na dakika kumi na tano. Saa ya hadi inaonesha saa kumi na mbili na dakika thelathini.",
            "pg125_n0019": "Muda uliotumika ni kiasi gani?",
            "pg125_n0020": "Andika muda uliotumika katika nafasi iliyo wazi.",
        },
    },
    126: {
        "rate": 0.85,
        "replace": {
            "pg126_n0001": "Sehemu b. Kuna michoro miwili ya saa. Saa ya kwanza ina namba za kawaida; mshale mrefu unaelekea namba tatu na mshale mfupi unaelekea namba nane. Saa ya pili ina namba za Kirumi; mshale mrefu unaelekea Roman kumi na mbili na mshale mfupi unaelekea Roman sita. Muda uliotumika ni kiasi gani?",
            "pg126_n0002": "Andika muda uliotumika katika nafasi iliyo wazi.",
            "pg126_n0003": "Sehemu c. Saa ya kidijitali ya kuanzia inaonesha saa moja kamili. Saa ya hadi inaonesha saa nane na dakika arobaini na tano. Muda uliotumika ni kiasi gani?",
            "pg126_n0004": "Andika muda uliotumika katika nafasi iliyo wazi.",
            "pg126_n0006": "Mfano.",
            "pg126_n0010": "Njia.",
            "pg126_n0011": "Muda unaotumika, sawa sawa na muda wa kumaliza, kutoa muda wa kuanza.",
            "pg126_n0012": "Saa kumi na dakika arobaini, kutoa saa mbili na dakika arobaini na tano.",
            "pg126_n0013": "Panga kwa wima katika safu ya saa na safu ya dakika.",
            "pg126_n0014": "Mstari wa juu: saa kumi na dakika arobaini.",
            "pg126_n0015": "Kutoa saa mbili na dakika arobaini na tano.",
            "pg126_n0016": "Jibu linalooneshwa ni saa saba na dakika hamsini na tano.",
            "pg126_n0017": "Hatua.",
            "pg126_n0018": "Hatua ya kwanza. Dakika arobaini ni chache kuliko dakika arobaini na tano.",
            "pg126_n0019": "Hatua ya pili. Chukua saa moja, ambayo ni dakika sitini, kutoka saa kumi.",
            "pg126_n0020": "Jumlisha dakika sitini na dakika arobaini, sawa sawa na dakika mia moja.",
        },
    },
    127: {
        "rate": 0.85,
        "remove": {"pg127_n0001"},
        "replace": {
            "pg127_n0002": "Hatua ya tatu. Toa dakika. Mia moja kutoa arobaini na tano, sawa sawa na hamsini na tano.",
            "pg127_n0003": "Hatua ya nne. Andika dakika hamsini na tano katika nafasi ya dakika.",
            "pg127_n0004": "Hatua ya tano. Baada ya kuchukua saa moja, zimebaki saa tisa. Toa saa: tisa kutoa mbili, sawa sawa na saba.",
            "pg127_n0005": "Hatua ya sita. Andika saba katika nafasi ya saa.",
            "pg127_n0006": "Kwa hiyo, muda unaotumika kukamilisha ratiba ya shule kwa siku ni saa saba na dakika hamsini na tano.",
            "pg127_n0008": "Zoezi la Saba.",
            "pg127_n0009": "Jibu maswali yafuatayo.",
            "pg127_n0010": "Swali namba moja. Rehema ni mwanafunzi wa darasa la nne katika shule ya msingi Mtakuja.",
            "pg127_n0011": "Baada ya masomo anatumia muda wa saa tatu na dakika kumi na tano kujisomea.",
            "pg127_n0012": "Ikiwa huanza kujisomea saa moja na dakika kumi na tano usiku,",
            "pg127_n0013": "anamaliza saa ngapi?",
            "pg127_n0014": "Swali namba mbili. Zakaria aliondoka nyumbani saa kumi na mbili na dakika thelathini asubuhi kwenda shuleni.",
            "pg127_n0015": "Alitumia muda wa dakika arobaini na tano kutembea. Je, alifika shuleni saa ngapi?",
            "pg127_n0017": "Swali namba tatu. Wachezaji wa mpira wa miguu walitumia saa moja na dakika thelathini kucheza mpira.",
            "pg127_n0018": "Ikiwa walianza kucheza saa kumi na mbili kamili jioni, je, walimaliza kucheza mpira saa ngapi?",
            "pg127_n0020": "Swali namba nne. Mwasi alifika shuleni saa kumi na mbili na dakika kumi na tano asubuhi akiwa amechelewa dakika kumi na tano.",
            "pg127_n0021": "Je, alitakiwa kufika shuleni saa ngapi?",
            "pg127_n0022": "Swali namba tano. Roza ni mtunza muda shuleni. Hugonga kengele kila baada ya dakika arobaini.",
            "pg127_n0023": "Iwapo aligonga kengele saa mbili na dakika arobaini asubuhi,",
            "pg127_n0024": "Roza atagonga tena kengele saa ngapi?",
            "pg127_n0025": "Swali namba sita. Mtihani ulianza saa tatu na dakika kumi na tano asubuhi na kumalizika saa sita na dakika kumi na tano mchana.",
            "pg127_n0026": "Mtihani huo ulifanyika kwa muda gani?",
        },
    },
    128: {
        "rate": 0.85,
        "remove": {"pg128_n0001"},
        "replace": {
            "pg128_n0002": "Swali namba saba. Kipindi cha somo la Hisabati cha dakika arobaini kilimalizika saa tano na dakika ishirini.",
            "pg128_n0003": "Kipindi kilianza saa ngapi?",
            "pg128_n0004": "Swali namba nane. Basi liliondoka stendi kuu ya Tanga saa kumi na mbili kamili asubuhi na kufika Dodoma saa kumi na moja na dakika arobaini na tano jioni.",
            "pg128_n0005": "Basi lilisafiri kwa muda gani?",
            "pg128_n0006": "Swali namba tisa. Vanesa alifika shuleni saa kumi na mbili na dakika kumi na tano asubuhi.",
            "pg128_n0007": "Alikuwa amewahi kwa saa moja na dakika arobaini na tano. Alitakiwa afike shuleni saa ngapi?",
            "pg128_n0008": "Swali namba kumi. Chagua herufi ya jibu sahihi kutoka Orodha B na uiandike katika Orodha A ili ilete maana.",
            "pg128_n0010": "Jedwali lina orodha mbili. Nitasoma Orodha A kwanza, kisha Orodha B. Usichague jibu mpaka usikie orodha zote.",
            "pg128_n0011": "Orodha A. Roman moja: dakika tisini.",
            "pg128_n0012": "Roman mbili: mshale mrefu wa saa.",
            "pg128_n0013": "Roman tatu: mshale mfupi wa saa.",
            "pg128_n0014": "Roman nne: dakika kumi na tano.",
            "pg128_n0015": "Roman tano: dakika thelathini.",
            "pg128_n0016": "Orodha B. a: unaonesha saa. b: robo saa. c: huonesha saa kumi na mbili. d: unaonesha dakika. e: dakika sitini. f: nusu saa. g: kasoro robo. h: saa moja na nusu.",
            "pg128_n0019": "Jikumbushe.",
            "pg128_n0020": "Jambo la kwanza. Katika uso wa saa, mshale mfupi huonesha saa, mshale mrefu huonesha dakika,",
            "pg128_n0021": "na mshale mrefu zaidi na mwembamba huonesha sekunde.",
            "pg128_n0023": "Jambo la pili. Saa moja ni sawa na dakika sitini.",
            "pg128_n0024": "Jambo la tatu. Dakika moja ni sawa na sekunde sitini.",
            "pg128_n0025": "Jambo la nne. Wiki moja ina siku saba.",
            "pg128_n0026": "Jambo la tano. Wakati hupimwa kwa kutumia vipimo rasmi na visivyo rasmi.",
            "pg128_n0027": "Jambo la sita. Mwaka mmoja ni sawa na miezi kumi na mbili.",
        },
    },
    129: {
        "rate": 0.85,
        "remove": {"pg129_n0020"},
        "replace": {
            "pg129_n0001": "Sura ya Kumi.",
            "pg129_n0016": "Kazi namba moja.",
            "pg129_n0018": "Hatua.",
            "pg129_n0019": "Hatua ya kwanza. Pima urefu wa uwanja kwa kutumia hatua za miguu kama inavyoonekana katika mchoro unaofuata.",
            "pg129_n0021": "Hatua ya pili. Pima upana wa uwanja kwa kutumia hatua za miguu.",
            "pg129_n0022": "Hatua ya tatu. Wanafunzi walinganishe idadi ya hatua walizorekodi.",
        },
    },
    130: {
        "rate": 0.85,
        "remove": {"pg130_n0017"},
        "replace": {
            "pg130_n0001": "Maelezo ya picha. Mwanafunzi anatembea kwa hatua zinazofuatana ili kupima urefu na upana wa uwanja. Kila hatua ya mguu hutumika kama kipimio kisicho rasmi.",
            "pg130_n0002": "Maswali.",
            "pg130_n0003": "Swali sehemu a. Je, umepata hatua ngapi za urefu wa uwanja?",
            "pg130_n0004": "Swali sehemu b. Je, umepata hatua ngapi za upana wa uwanja?",
            "pg130_n0012": "Kazi namba mbili.",
            "pg130_n0014": "Hatua.",
            "pg130_n0015": "Hatua ya kwanza. Linganisha mwanzo wa rula na pembe ya mwanzo ya kitabu,",
            "pg130_n0016": "ili alama ya sifuri ya rula ilingane na pembe ya kitabu, kama inavyoonekana katika mchoro unaofuata.",
        },
    },
    131: {
        "rate": 0.85,
        "replace": {
            "pg131_n0001": "Maelezo ya picha. Kitabu kimewekwa sambamba juu ya rula. Pembe yake ya mwanzo inalingana na alama ya sifuri, na pembe ya mwisho inaonesha mahali pa kusoma urefu kwa sentimita.",
            "pg131_n0002": "Hatua ya pili. Hesabu sentimita kuanzia kona ya mwanzo wa kitabu hadi kona ya mwisho wa kitabu.",
            "pg131_n0003": "Je, umepata sentimita ngapi?",
            "pg131_n0005": "Hatua ya tatu. Andika kipimo katika sentimita.",
            "pg131_n0010": "Tofauti kati ya vipimio rasmi na visivyo rasmi.",
            "pg131_n0011": "Jambo la kwanza. Vipimio visivyo rasmi hutumiwa katika jamii fulani kwa makubaliano yao.",
            "pg131_n0013": "Jambo la pili. Vipimio visivyo rasmi vinatofautiana kati ya kipimio kimoja na kingine.",
            "pg131_n0015": "Jambo la tatu. Vipimio rasmi vinafanana kati ya kipimio kimoja na kingine.",
            "pg131_n0017": "Jambo la nne. Vipimio rasmi hutumika kitaifa na kimataifa.",
        },
    },
    132: {
        "rate": 0.85,
        "remove": {"pg132_n0021", "pg132_n0022", "pg132_n0024", "pg132_n0025", "pg132_n0026", "pg132_n0027", "pg132_n0028", "pg132_n0029", "pg132_n0030", "pg132_n0031", "pg132_n0032", "pg132_n0033", "pg132_n0034", "pg132_n0035"},
        "replace": {
            "pg132_n0001": "Zoezi la Kwanza.",
            "pg132_n0002": "Jibu maswali yafuatayo.",
            "pg132_n0003": "Swali namba moja. Pima na rekodi urefu wa vitu vitatu tofauti kwa kutumia vipimio rasmi.",
            "pg132_n0005": "Swali namba mbili. Pima na rekodi urefu wa vitu vitatu tofauti kwa kutumia vipimio visivyo rasmi.",
            "pg132_n0007": "Swali namba tatu. Orodhesha vipimio vya urefu visivyo rasmi vilivyoko kwenye mazingira yako.",
            "pg132_n0010": "Kipimo cha msingi cha urefu ni mita, kifupi chake ni herufi m.",
            "pg132_n0011": "Vipimo vingine ni milimita, kifupi m m; sentimita, kifupi s m;",
            "pg132_n0012": "na kilomita, kifupi k m.",
            "pg132_n0015": "Sehemu a. Sentimita moja, sawa sawa na milimita kumi.",
            "pg132_n0016": "Sehemu b. Mita moja, sawa sawa na sentimita mia moja.",
            "pg132_n0017": "Sehemu c. Mita moja, sawa sawa na milimita elfu moja.",
            "pg132_n0018": "Sehemu d. Kilomita moja, sawa sawa na mita elfu moja.",
            "pg132_n0020": "Mifano miwili. Tutasoma mfano mmoja ukamilike kabla ya mwingine. Mfano wa kwanza. Badili kilomita tano na mita mia mbili hamsini kuwa mita. Njia. Kilomita moja ni mita elfu moja. Kilomita tano ni mita elfu moja kuzidisha tano, sawa sawa na mita elfu tano. Jumlisha mita elfu tano na mita mia mbili hamsini; unapata mita elfu tano mia mbili hamsini. Kwa hiyo, kilomita tano na mita mia mbili hamsini, sawa sawa na mita elfu tano mia mbili hamsini. Mfano wa pili. Badili mita tatu kuwa sentimita. Njia. Mita moja ni sentimita mia moja. Mita tatu ni sentimita mia moja kuzidisha tatu, sawa sawa na sentimita mia tatu. Kwa hiyo, mita tatu, sawa sawa na sentimita mia tatu.",
        },
    },
    133: {
        "rate": 0.85,
        "remove": {"pg133_n0011", "pg133_n0013", "pg133_n0014", "pg133_n0015", "pg133_n0016", "pg133_n0017", "pg133_n0018", "pg133_n0019", "pg133_n0020", "pg133_n0021"},
        "replace": {
            "pg133_n0001": "Zoezi la Pili.",
            "pg133_n0002": "Jibu maswali yafuatayo.",
            "pg133_n0003": "Swali namba moja. Badili kilomita kuwa mita.",
            "pg133_n0004": "Sehemu a, kilomita thelathini na sita. Sehemu b, kilomita thelathini na tano na mita ishirini. Sehemu c, kilomita thelathini na nne na mita kumi na tano. Sehemu d, kilomita saba na mita mia tano.",
            "pg133_n0005": "Swali namba mbili. Badili mita kuwa sentimita.",
            "pg133_n0006": "Sehemu a, mita elfu mbili mia moja. Sehemu b, mita mia tisa tisini. Sehemu c, mita sitini na mbili na sentimita arobaini. Sehemu d, mita mia tatu arobaini na moja na sentimita tisa.",
            "pg133_n0007": "Swali namba tatu. Badili sentimita kuwa milimita.",
            "pg133_n0008": "Sehemu a, sentimita tano. Sehemu b, sentimita mia moja na mbili. Sehemu c, sentimita hamsini na milimita nane. Sehemu d, sentimita mia tisa na milimita tisini.",
            "pg133_n0010": "Mifano miwili. Mfano wa kwanza. Badili sentimita mia tano kuwa mita. Njia. Mita moja ni sentimita mia moja. Sentimita mia tano ni mita mia tano kugawanya mia moja, sawa sawa na mita tano. Kwa hiyo, sentimita mia tano, sawa sawa na mita tano. Mfano wa pili. Badili mita elfu nne mia tano kuwa kilomita. Njia. Kilomita moja ni mita elfu moja. Mita elfu nne mia tano ni kilomita elfu nne mia tano kugawanya elfu moja, sawa sawa na kilomita nne na mita mia tano. Kwa hiyo, mita elfu nne mia tano, sawa sawa na kilomita nne na mita mia tano.",
            "pg133_n0022": "Zoezi la Tatu.",
            "pg133_n0023": "Jibu maswali yafuatayo.",
            "pg133_n0024": "Swali namba moja. Badili mita kuwa kilomita.",
            "pg133_n0025": "Sehemu a, mita elfu tisa. Sehemu b, mita elfu moja mia saba hamsini. Sehemu c, mita elfu tisa mia saba hamsini. Sehemu d, mita elfu moja ishirini na tano.",
            "pg133_n0026": "Swali namba mbili. Badili sentimita kuwa mita.",
            "pg133_n0027": "Sehemu a, sentimita elfu mbili. Sehemu b, sentimita elfu moja mia tano hamsini. Sehemu c, sentimita mia tatu ishirini na tano. Sehemu d, sentimita elfu mbili ishirini na tano.",
        },
    },
    134: {
        "rate": 0.85,
        "remove": {"pg134_n0011", "pg134_n0012", "pg134_n0013", "pg134_n0014", "pg134_n0015", "pg134_n0016", "pg134_n0017", "pg134_n0018", "pg134_n0019", "pg134_n0020", "pg134_n0021", "pg134_n0022", "pg134_n0023", "pg134_n0024", "pg134_n0025"},
        "replace": {
            "pg134_n0001": "Swali namba tatu. Badili milimita kuwa sentimita.",
            "pg134_n0002": "Sehemu a, milimita arobaini. Sehemu b, milimita mia mbili arobaini na tano. Sehemu c, milimita mia tano. Sehemu d, milimita mia tano hamsini.",
            "pg134_n0004": "Mfano.",
            "pg134_n0005": "Fausta alitembea kilomita nane na mita mia saba kutoka sokoni hadi kazini kwake.",
            "pg134_n0006": "Tasha alitembea mita elfu sita mia tisa ishirini na nane kutoka sokoni hadi nyumbani kwake.",
            "pg134_n0008": "Sehemu a. Nani alitembea umbali mrefu zaidi?",
            "pg134_n0009": "Sehemu b. Kutokana na jibu la sehemu a, alitembea kwa umbali wa mita ngapi zaidi?",
            "pg134_n0010": "Njia ya sehemu a. Badili umbali wa Fausta kuwa mita. Kilomita moja ni mita elfu moja. Kilomita nane ni mita elfu moja kuzidisha nane, sawa sawa na mita elfu nane. Jumlisha mita elfu nane na mita mia saba, sawa sawa na mita elfu nane mia saba. Linganisha mita elfu nane mia saba na mita elfu sita mia tisa ishirini na nane. Mita elfu nane mia saba ni kubwa zaidi; kwa hiyo Fausta alitembea umbali mrefu zaidi. Njia ya sehemu b. Mita elfu nane mia saba kutoa mita elfu sita mia tisa ishirini na nane, sawa sawa na mita elfu moja mia saba sabini na mbili. Kwa hiyo, Fausta alitembea mita elfu moja mia saba sabini na mbili zaidi.",
        },
    },
    135: {
        "rate": 0.85,
        "replace": {
            "pg135_n0001": "Zoezi la Nne.",
            "pg135_n0002": "Jibu maswali yafuatayo.",
            "pg135_n0003": "Swali namba moja. Urefu wa chumba cha darasa la nne ni mita sita na sentimita sabini na tano.",
            "pg135_n0004": "Tafuta urefu wa darasa hilo katika sentimita.",
            "pg135_n0005": "Swali namba mbili. Umbali kutoka soko la Mtakuja hadi Ziwa Tanganyika ni kilomita kumi na mbili.",
            "pg135_n0006": "Umbali huo ni mita ngapi?",
            "pg135_n0007": "Swali namba tatu. Bulali alinunua kitambaa cha mita hamsini. Kulwa alinunua kitambaa cha sentimita mia mbili.",
            "pg135_n0008": "Nani alinunua kitambaa kirefu zaidi?",
            "pg135_n0010": "Swali namba nne. Umbali kutoka shuleni hadi zahanati ni mita mia nane.",
            "pg135_n0011": "Umbali kutoka shuleni hadi sokoni ni kilomita moja. Ni wapi mbali zaidi kutoka shuleni?",
            "pg135_n0013": "Swali namba tano. Sadoki hutembea mita elfu mbili kutoka nyumbani hadi shuleni.",
            "pg135_n0014": "Je, anatembea umbali gani kwenda shuleni na kurudi?",
            "pg135_n0015": "Swali namba sita. Hashimu alikula muwa wenye urefu wa sentimita mia moja ishirini na nane, na Rehema alikula muwa wenye urefu wa mita moja.",
            "pg135_n0017": "Nani alikula muwa mrefu zaidi?",
            "pg135_n0018": "Swali namba saba. Umbali kutoka chumba cha darasa la nne hadi uwanja wa mpira ni sentimita elfu saba.",
            "pg135_n0019": "Umbali kutoka chumba cha darasa la nne hadi ofisi ya mwalimu mkuu ni mita sabini.",
            "pg135_n0021": "Umbali upi ni mrefu zaidi?",
            "pg135_n0022": "Swali namba nane. Bahati hutembea kilomita tatu na mita mia tano kila asubuhi, na kilomita moja na mita mia tano kila jioni.",
            "pg135_n0023": "Doto hutembea kilomita tano kila asubuhi. Nani anatembea umbali mrefu zaidi?",
        },
    },
    136: {
        "rate": 0.85,
        "replace": {
            "pg136_n0010": "Kazi namba tatu.",
            "pg136_n0011": "Kuchunguza uzito wa vitu kwa kutumia ndoo kama inavyoonekana katika picha.",
            "pg136_n0013": "Hatua.",
            "pg136_n0014": "Hatua ya kwanza. Chukua ndoo mbili, kisha weka pumba za mahindi ndani yake kama inavyoonekana.",
            "pg136_n0016": "Maelezo ya picha. Kuna ndoo mbili nyekundu. Ndoo ya kwanza ina pumba karibu na ukingo wake. Ndoo ya pili ina pumba nyingi zaidi, zilizoinuka juu ya ukingo. Picha inaonesha tofauti ya kiasi, lakini mwanafunzi atazitumia kutambua tofauti ya uzito.",
            "pg136_n0018": "Hatua ya pili. Nyanyua ndoo ya kwanza, kisha nyanyua ndoo ya pili.",
            "pg136_n0019": "Hatua ya tatu. Je, ndoo ipi ni nzito zaidi?",
        },
    },
    137: {
        "rate": 0.85,
        "replace": {
            "pg137_n0005": "Aina za mizani. Maelezo ya picha. Kutoka kushoto kwenda kulia kuna mizani ya kusimamia yenye kioo cha kuonesha uzito, mizani ya kuning'iniza yenye ndoano, na mizani ya msawazo yenye sinia mbili.",
            "pg137_n0009": "Kazi namba nne.",
            "pg137_n0011": "Hatua.",
            "pg137_n0012": "Hatua ya kwanza. Pima uzito wa kasha moja la chaki, kitabu cha Hisabati, na kipande cha tofali kwa kutumia mizani.",
            "pg137_n0014": "Hatua ya pili. Je, umepata kilogramu ngapi kwa kila kifaa?",
            "pg137_n0015": "Hatua ya tatu. Rekodi uzito wa vifaa hivyo katika kilogramu.",
            "pg137_n0017": "Kipimo cha msingi cha uzito ni kilogramu, kifupi k g.",
            "pg137_n0018": "Vipimo vingine ni gramu, kifupi g; na miligramu, kifupi m g.",
            "pg137_n0019": "Gramu moja, sawa sawa na miligramu elfu moja.",
            "pg137_n0020": "Kilogramu moja, sawa sawa na gramu elfu moja.",
        },
    },
    138: {
        "rate": 0.85,
        "remove": {"pg138_n0013", "pg138_n0014", "pg138_n0015", "pg138_n0016", "pg138_n0017", "pg138_n0018"},
        "replace": {
            "pg138_n0001": "Kazi namba tano.",
            "pg138_n0003": "Hatua.",
            "pg138_n0004": "Hatua ya kwanza. Andaa mchanga na mizani. Maelezo ya picha. Kuna mizani ya msawazo na vizani vinne vya kilogramu tano, kilogramu mbili, gramu mia tano na gramu mia mbili hamsini.",
            "pg138_n0005": "Hatua ya pili. Pima mchanga kiasi cha kilogramu mbili na nusu kwenye mizani.",
            "pg138_n0006": "Hatua ya tatu. Linganisha uzani hadi mizani ionyeshe kilogramu mbili na nusu.",
            "pg138_n0007": "Hatua ya nne. Andika kipimo cha mchanga kwa gramu na kwa kilogramu.",
            "pg138_n0012": "Mifano miwili. Mfano wa kwanza. Badili kilogramu nne kuwa gramu. Njia. Kilogramu moja ni gramu elfu moja. Kilogramu nne ni gramu elfu moja kuzidisha nne, sawa sawa na gramu elfu nne. Kwa hiyo, kilogramu nne, sawa sawa na gramu elfu nne. Mfano wa pili. Badili gramu elfu saba kuwa kilogramu. Njia. Kilogramu moja ni gramu elfu moja. Gramu elfu saba ni kilogramu elfu saba kugawanya elfu moja, sawa sawa na kilogramu saba. Kwa hiyo, gramu elfu saba, sawa sawa na kilogramu saba.",
        },
    },
    139: {
        "rate": 0.85,
        "remove": {"pg139_n0005", "pg139_n0015", "pg139_n0016", "pg139_n0017", "pg139_n0018", "pg139_n0019", "pg139_n0020", "pg139_n0021", "pg139_n0022", "pg139_n0023"},
        "replace": {
            "pg139_n0001": "Zoezi la Tano.",
            "pg139_n0002": "Jibu maswali yafuatayo.",
            "pg139_n0003": "Swali namba moja. Jaza nafasi zilizoachwa wazi katika jedwali.",
            "pg139_n0004": "Jedwali lina mistari miwili: kilogramu na gramu. Safu ya kwanza: kilogramu moja, sawa sawa na gramu elfu moja. Safu ya pili: kilogramu ni nafasi wazi; gramu elfu mbili. Safu ya tatu: kilogramu tatu; gramu ni nafasi wazi. Safu ya nne: kilogramu ni nafasi wazi; gramu elfu nne. Safu ya tano: kilogramu tano; gramu ni nafasi wazi. Safu ya sita: kilogramu ni nafasi wazi; gramu elfu sita. Safu ya saba: kilogramu saba; gramu ni nafasi wazi. Safu ya nane: kilogramu ni nafasi wazi; gramu elfu nane. Safu ya tisa: kilogramu tisa; gramu ni nafasi wazi. Safu ya kumi: kilogramu ni nafasi wazi; gramu elfu kumi.",
            "pg139_n0006": "Swali namba mbili. Badili kilogramu kuwa gramu.",
            "pg139_n0007": "Sehemu a, kilogramu mbili. Sehemu b, kilogramu tatu. Sehemu c, kilogramu arobaini na tano. Sehemu d, kilogramu themanini na tisa.",
            "pg139_n0008": "Swali namba tatu. Badili gramu kuwa kilogramu.",
            "pg139_n0009": "Sehemu a, gramu elfu kumi na tano. Sehemu b, gramu elfu sitini na nne. Sehemu c, gramu elfu arobaini na mbili. Sehemu d, gramu elfu hamsini na nane.",
            "pg139_n0011": "Mfano.",
            "pg139_n0012": "Uzito wa Idi ni kilogramu ishirini na nne, na uzito wa Penina ni gramu elfu ishirini na nne mia nne hamsini.",
            "pg139_n0013": "Nani ana uzito mkubwa zaidi?",
            "pg139_n0014": "Hatua. Hatua ya kwanza. Tambua vipimo: Idi ana kilogramu ishirini na nne; Penina ana gramu elfu ishirini na nne mia nne hamsini. Hatua ya pili. Badili uzito wa Idi kuwa gramu. Kilogramu moja ni gramu elfu moja. Kilogramu ishirini na nne ni gramu elfu moja kuzidisha ishirini na nne, sawa sawa na gramu elfu ishirini na nne. Hatua ya tatu. Linganisha gramu elfu ishirini na nne na gramu elfu ishirini na nne mia nne hamsini. Gramu elfu ishirini na nne mia nne hamsini ni kubwa zaidi. Kwa hiyo, Penina ana uzito mkubwa zaidi.",
        },
    },
    140: {
        "rate": 0.85,
        "replace": {
            "pg140_n0001": "Zoezi la Sita.",
            "pg140_n0002": "Jibu maswali yafuatayo.",
            "pg140_n0003": "Swali namba moja. Badili gramu elfu tano mia mbili hamsini kuwa kilogramu.",
            "pg140_n0004": "Swali namba mbili. Ipi ni nzito zaidi, gramu elfu mbili au kilogramu ishirini?",
            "pg140_n0005": "Swali namba tatu. Kuna gramu ngapi katika kilogramu mbili?",
            "pg140_n0006": "Swali namba nne. Ipi nzito zaidi, kilogramu moja ya chumvi au kilogramu moja ya pamba?",
            "pg140_n0007": "Swali namba tano. Pepe alinunua kilogramu tatu na gramu mia tano za samaki.",
            "pg140_n0008": "Alinunua gramu ngapi za samaki?",
            "pg140_n0009": "Swali namba sita. Elia alinunua nusu kilogramu na robo kilogramu za mchele.",
            "pg140_n0010": "Mchele alionunua ulikuwa na uzito wa gramu ngapi?",
            "pg140_n0011": "Swali namba saba. Mao, Zawadi na Furaha walipima uzito wao.",
            "pg140_n0012": "Mao alikuwa na kilogramu thelathini na mbili; Zawadi kilogramu thelathini; na Furaha gramu elfu thelathini mia saba hamsini.",
            "pg140_n0013": "Sehemu a. Nani ana uzito mkubwa?",
            "pg140_n0014": "Sehemu b. Nani ana uzito mdogo?",
            "pg140_n0015": "Swali namba nane. Bibi alinunua kilogramu mbili za unga wa mtama, kilogramu moja ya sukari, na gramu mia tano za maziwa ya unga.",
            "pg140_n0016": "Jumla alinunua gramu ngapi za vitu vyote?",
            "pg140_n0018": "Swali namba tisa. Mkate mmoja una uzito wa nusu kilogramu. Tafuta uzito wa mikate mitano katika gramu.",
            "pg140_n0020": "Swali namba kumi. Dada alinunua nyanya kilogramu mbili na vitunguu kilogramu moja, vikawekwa ndani ya kikapu.",
            "pg140_n0022": "Kikapu hicho kilikuwa na vitu vyenye uzito wa gramu ngapi?",
            "pg140_n0023": "Swali namba kumi na moja. Uzito wa Adamu ni kilogramu thelathini na nne, na uzito wa Kateri ni gramu elfu thelathini na nne mia saba. Nani ana uzito mkubwa zaidi?",
            "pg140_n0025": "Swali namba kumi na mbili. Uzito wa kuku ni kilogramu tatu. Baada ya kumuandaa kwa mapishi alikuwa na kilogramu mbili na gramu mia saba hamsini.",
            "pg140_n0026": "Uzito wake ulipungua kwa kiasi gani? Kwa nini?",
        },
    },
    141: {
        "rate": 0.85,
        "remove": {"pg141_n0005", "pg141_n0006", "pg141_n0007", "pg141_n0008", "pg141_n0018", "pg141_n0019", "pg141_n0020", "pg141_n0021"},
        "replace": {
            "pg141_n0002": "Kipimo cha msingi cha ujazo ni lita, kifupi herufi l. Kipimo kingine ni mililita, kifupi m l.",
            "pg141_n0004": "Lita moja, sawa sawa na mililita elfu moja.",
            "pg141_n0009": "Maelezo ya picha. Kuna chombo cha mafuta cha lita moja, chombo cha mafuta cha lita nne, na tanki la maji la lita elfu tatu. Vyombo vina ukubwa tofauti kulingana na ujazo wake. Kazi namba sita.",
            "pg141_n0011": "Hatua.",
            "pg141_n0012": "Hatua ya kwanza. Jaza maji kwenye jagi mpaka ukomo wake. Tumia jagi hilo kujaza ndoo yenye ujazo wa lita kumi.",
            "pg141_n0014": "Hatua ya pili. Jagi ngapi za maji zimejaza ndoo hiyo?",
            "pg141_n0015": "Hatua ya tatu. Jagi hilo lina ujazo wa lita ngapi?",
            "pg141_n0016": "Zoezi la Saba.",
            "pg141_n0017": "Chunguza chati ifuatayo, kisha jibu maswali. Chati ina vitu vinane, vilivyopangwa katika mistari miwili. Mstari wa kwanza: jagi, lita, chupa na mizani ya msawazo. Mstari wa pili: rula ndefu, boksi, bomba la sindano na ndoo ya maji.",
        },
    },
    142: {
        "rate": 0.85,
        "replace": {
            "pg142_n0001": "Swali namba moja. Vipimio vipi vinatumika kupima ujazo?",
            "pg142_n0002": "Swali namba mbili. Kipimo kipi kinapima ujazo?",
            "pg142_n0003": "Swali namba tatu. Orodhesha vipimio vinavyopima:",
            "pg142_n0004": "sehemu a, ujazo mkubwa;",
            "pg142_n0005": "sehemu b, ujazo mdogo.",
            "pg142_n0006": "Swali namba nne. Soma taarifa ifuatayo, kisha jibu maswali.",
            "pg142_n0007": "Faraja alipima juisi yenye ujazo wa mililita mia moja hamsini akamimina kwenye chupa, kisha akapumzika.",
            "pg142_n0008": "Alikunywa kiasi na kubakiza mililita sitini na tano.",
            "pg142_n0009": "Baada ya kupumzika akaongeza mililita mia mbili ishirini kwenye chupa hiyo.",
            "pg142_n0010": "Baadaye akanywa tena na akabakiza mililita ishirini na tano za juisi.",
            "pg142_n0011": "Sehemu a. Faraja alikunywa juisi kiasi gani mara ya kwanza?",
            "pg142_n0012": "Sehemu b. Aliongeza kiasi gani cha juisi kwenye chupa?",
            "pg142_n0013": "Sehemu c. Alikunywa kiasi gani mara ya pili?",
            "pg142_n0014": "Sehemu d. Jumla alikunywa kiasi gani cha juisi?",
            "pg142_n0015": "Sehemu e. Kiasi gani cha juisi kilibaki?",
            "pg142_n0017": "Mfano.",
            "pg142_n0018": "Ng'ombe hutoa lita ishirini za maziwa kila siku. Atatoa lita ngapi za maziwa kwa siku tatu?",
            "pg142_n0020": "Hatua.",
            "pg142_n0021": "Hatua ya kwanza. Siku moja, sawa sawa na lita ishirini.",
            "pg142_n0022": "Hatua ya pili. Siku tatu, sawa sawa na lita ishirini kuzidisha tatu, sawa sawa na lita sitini.",
            "pg142_n0023": "Kwa hiyo, ng'ombe atatoa lita sitini za maziwa kwa siku tatu.",
        },
    },
    143: {
        "rate": 0.85,
        "replace": {
            "pg143_n0001": "Zoezi la Nane.",
            "pg143_n0002": "Jibu maswali yafuatayo.",
            "pg143_n0003": "Swali namba moja. Lita moja ya mafuta inauzwa shilingi elfu nne.",
            "pg143_n0004": "Lita tatu za mafuta zitauzwa shilingi ngapi?",
            "pg143_n0005": "Swali namba mbili. Panga kuanzia kipimo kidogo hadi kikubwa zaidi: mililita mia nne hamsini, mililita arobaini, mililita nne, na mililita mia nne.",
            "pg143_n0007": "Swali namba tatu. Mtungi wa gesi una ujazo wa lita tano. Iwapo lita tatu zimetumika, zimebaki lita ngapi?",
            "pg143_n0009": "Swali namba nne. Chupa ngapi za maji zenye ujazo wa mililita mia tano zitahitajika kujaza ndoo ya lita ishirini?",
            "pg143_n0011": "Swali namba tano. Ndoo ngapi za maji zenye ujazo wa lita tano zitahitajika kujaza tanki la lita mia tano?",
            "pg143_n0013": "Swali namba sita. Chupa ya mililita elfu moja ina maziwa mililita mia saba hamsini.",
            "pg143_n0014": "Kiasi gani zaidi kitahitajika kujaza chupa hiyo?",
            "pg143_n0015": "Swali namba saba. Lina, Sanka na Imani walijaza ndoo ya maji.",
            "pg143_n0016": "Lina aliweka lita tano, Sanka lita mbili, na Imani lita tatu.",
            "pg143_n0017": "Je, kwa pamoja wote waliweka kiasi gani cha maji?",
            "pg143_n0018": "Swali namba nane. Sia alinunua juisi mililita elfu moja mia tano. Iwapo alikunywa mililita mia tano,",
            "pg143_n0019": "alibakiza mililita ngapi za juisi?",
            "pg143_n0020": "Swali namba tisa. Mbale anakunywa lita tatu za maji na Senga anakunywa mililita elfu mbili za maji.",
            "pg143_n0021": "Kati yao nani anakunywa maji mengi zaidi? Kwa kiasi gani zaidi?",
        },
    },
    144: {
        "rate": 0.85,
        "replace": {
            "pg144_n0001": "Swali namba kumi. Oanisha na andika maneno kutoka Kifungu A na yale ya Kifungu B ili kuleta maana.",
            "pg144_n0003": "Jedwali lina vifungu viwili. Nitasoma Kifungu A kwanza, kisha Kifungu B.",
            "pg144_n0004": "Kifungu A. Roman moja: vipimo.",
            "pg144_n0005": "Roman mbili: uzani.",
            "pg144_n0006": "Roman tatu: urefu.",
            "pg144_n0007": "Roman nne: ujazo.",
            "pg144_n0008": "Roman tano: vipimio.",
            "pg144_n0009": "Kifungu B. a: vifaa vya kupimia. b: mkusanyiko wa watu. c: mita, gramu na lita. d: uzito wa kitu. e: penseli ya kuchorea. f: umbali kati ya vitu viwili. g: kiasi cha kimiminika.",
            "pg144_n0011": "Jikumbushe.",
            "pg144_n0012": "Jambo la kwanza. Kipimo cha msingi cha urefu ni mita, kifupi m.",
            "pg144_n0013": "Jambo la pili. Kipimo cha msingi cha uzani ni gramu, kifupi g.",
            "pg144_n0014": "Jambo la tatu. Kipimo cha msingi cha ujazo ni lita, kifupi l.",
        },
    },
    145: {
        "rate": 0.85,
        "replace": {
            "pg145_n0001": "Sura ya Kumi na Moja.",
            "pg145_n0013": "Zoezi la Kwanza: Marudio.",
            "pg145_n0014": "Chunguza sarafu za Tanzania zifuatazo, kisha jibu maswali yanayofuata.",
            "pg145_n0016": "Maelezo ya sarafu. Mstari wa kwanza una pande mbili za sarafu ya shilingi mia tano: upande mmoja una picha ya kiongozi, na upande mwingine una picha ya nyati pamoja na namba mia tano.",
            "pg145_n0017": "Mstari wa pili una pande mbili za sarafu ya shilingi mia mbili: upande mmoja una picha ya kiongozi, na upande mwingine una wanyama pamoja na namba mia mbili.",
        },
    },
    146: {
        "rate": 0.85,
        "replace": {
            "pg146_n0001": "Maelezo ya sarafu yanaendelea. Mstari wa kwanza una pande mbili za sarafu ya shilingi mia moja: upande mmoja una picha ya kiongozi, na upande mwingine una wanyama pamoja na namba mia moja.",
            "pg146_n0002": "Mstari wa pili una pande mbili za sarafu ya shilingi hamsini: upande mmoja una picha ya kiongozi, na upande mwingine una kifaru pamoja na namba hamsini.",
            "pg146_n0003": "Mstari wa tatu una pande mbili za sarafu ya shilingi ishirini: upande mmoja una picha ya kiongozi, na upande mwingine una picha ya tembo pamoja na namba ishirini.",
            "pg146_n0004": "Mstari wa nne una pande mbili za sarafu ya shilingi kumi: upande mmoja una picha ya kiongozi, na upande mwingine una alama pamoja na namba kumi.",
        },
    },
    147: {
        "rate": 0.85,
        "remove": {"pg147_n0009", "pg147_n0010", "pg147_n0011"},
        "replace": {
            "pg147_n0001": "Maswali.",
            "pg147_n0002": "Swali namba moja. Je, sarafu yenye thamani kubwa kuliko zote ni ipi?",
            "pg147_n0003": "Swali namba mbili. Je, ni sarafu ipi ina thamani ndogo kuliko zote?",
            "pg147_n0004": "Swali namba tatu. Je, ni sarafu zipi umewahi kuziona?",
            "pg147_n0005": "Swali namba nne. Je, ni sarafu zipi umewahi kuzitumia kununulia vitu?",
            "pg147_n0007": "Zoezi la Pili.",
            "pg147_n0008": "Chunguza bei za bidhaa, kisha jibu maswali yanayofuata. Fuata picha na bei zake zilizo kwenye ukurasa; sauti haitatafsiri bidhaa kwa niaba yako.",
            "pg147_n0012": "Maswali.",
            "pg147_n0013": "Swali namba moja. Ni bidhaa ipi yenye bei kubwa kuliko zote?",
            "pg147_n0014": "Swali namba mbili. Kati ya sahani na sufuria, kipi chenye bei kubwa zaidi?",
            "pg147_n0015": "Swali namba tatu. Bei ya mkate ni shilingi ngapi?",
            "pg147_n0016": "Swali namba nne. Ni bidhaa ipi yenye bei ndogo kuliko zote?",
            "pg147_n0017": "Swali namba tano. Ni bidhaa zipi zina bei sawa?",
        },
    },
    148: {
        "rate": 0.85,
        "remove": {
            "pg148_n0007", "pg148_n0008", "pg148_n0009", "pg148_n0010", "pg148_n0011", "pg148_n0012",
            "pg148_n0013", "pg148_n0014", "pg148_n0015", "pg148_n0016", "pg148_n0017", "pg148_n0018",
            "pg148_n0019", "pg148_n0020", "pg148_n0021", "pg148_n0022", "pg148_n0023", "pg148_n0024",
        },
        "after": {
            "pg148_n0006": [
                "Mchoro unaonesha noti za Tanzania kwa mistari minne. Kila mstari una upande wa mbele na upande wa nyuma wa noti yenye thamani sawa.",
                "Mstari wa kwanza una noti ya shilingi mia tano. Mstari wa pili una noti ya shilingi elfu moja. Mstari wa tatu una noti ya shilingi elfu mbili. Mstari wa nne una noti ya shilingi elfu tano.",
            ],
        },
    },
    149: {
        "rate": 0.85,
        "remove": {"pg149_n0001", "pg149_n0002", "pg149_n0003", "pg149_n0004", "pg149_n0005", "pg149_n0020", "pg149_n0022", "pg149_n0024", "pg149_n0025", "pg149_n0026", "pg149_n0027"},
        "replace": {
            "pg149_n0006": "Maelezo ya picha yanakamilika. Mstari wa mwisho una pande mbili za noti ya shilingi elfu kumi. Maswali.",
            "pg149_n0007": "Swali namba moja. Taja noti yenye thamani kubwa kuliko zote.",
            "pg149_n0008": "Swali namba mbili. Ni noti ipi thamani yake inalingana na thamani ya sarafu mojawapo?",
            "pg149_n0010": "Swali namba tatu. Noti ipi ina thamani ndogo kuliko zote?",
            "pg149_n0011": "Swali namba nne. Taja alama tatu zilizopo katika noti ya shilingi elfu tano.",
            "pg149_n0012": "Swali namba tano. Taja alama tatu zilizopo katika noti ya shilingi elfu mbili.",
            "pg149_n0013": "Swali namba sita. Taja alama tano zilizopo katika noti ya shilingi elfu moja.",
            "pg149_n0018": "Mfano.",
            "pg149_n0019": "Sehemu a. Shilingi elfu sabini na moja mia nne, jumlisha shilingi elfu ishirini na nne mia tano, sawa sawa na shilingi elfu tisini na tano mia tisa.",
            "pg149_n0021": "Sehemu b. Shilingi elfu kumi na tisa mia nane hamsini, jumlisha shilingi elfu arobaini na tano mia tatu hamsini, sawa sawa na shilingi elfu sitini na tano mia mbili.",
            "pg149_n0023": "Sehemu c. Hesabu imepangwa kwa wima. Mstari wa juu ni shilingi elfu kumi na moja mia sita hamsini. Chini yake ni jumlisha shilingi elfu sabini na nane mia nne hamsini. Jibu linalooneshwa chini ya mstari ni shilingi elfu tisini mia moja.",
        },
    },
    150: {
        "rate": 0.85,
        "remove": {"pg150_n0004", "pg150_n0005", "pg150_n0006", "pg150_n0007", "pg150_n0008", "pg150_n0009", "pg150_n0010", "pg150_n0011", "pg150_n0012", "pg150_n0013", "pg150_n0014", "pg150_n0015", "pg150_n0016", "pg150_n0017", "pg150_n0018", "pg150_n0019", "pg150_n0020", "pg150_n0021", "pg150_n0022", "pg150_n0023", "pg150_n0024", "pg150_n0025", "pg150_n0026", "pg150_n0027", "pg150_n0028", "pg150_n0029", "pg150_n0030", "pg150_n0031", "pg150_n0032"},
        "replace": {
            "pg150_n0001": "Zoezi la Nne.",
            "pg150_n0002": "Jibu maswali yafuatayo. Maswali ya kwanza hadi ya nane yameandikwa kwa ulalo; ya tisa hadi ya ishirini yamepangwa kwa wima.",
            "pg150_n0003": "Swali namba moja. Shilingi elfu ishirini na tano mia tatu, jumlisha shilingi elfu sitini mia mbili, sawa sawa na ngapi? Swali namba mbili. Shilingi elfu hamsini na mbili mia sita sabini, jumlisha shilingi elfu kumi na saba mia tatu themanini, sawa sawa na ngapi? Swali namba tatu. Shilingi elfu thelathini na sita mia nane, jumlisha shilingi elfu arobaini na nne, sawa sawa na ngapi? Swali namba nne. Shilingi elfu kumi na moja mia tano, jumlisha shilingi elfu themanini mia moja hamsini, sawa sawa na ngapi? Swali namba tano. Shilingi elfu sitini na sita, jumlisha shilingi elfu tatu mia tano, sawa sawa na ngapi? Swali namba sita. Shilingi elfu ishirini na saba mia nane, jumlisha shilingi elfu sabini na moja hamsini, sawa sawa na ngapi? Swali namba saba. Shilingi elfu hamsini na nne hamsini, jumlisha shilingi elfu kumi na moja mia nne hamsini, sawa sawa na ngapi? Swali namba nane. Shilingi elfu sabini na tano, jumlisha shilingi elfu tatu mia tisa, sawa sawa na ngapi? Swali namba tisa. Kwa wima: shilingi elfu ishirini na saba mia nane, jumlisha shilingi elfu thelathini na tisa mia nne. Swali namba kumi. Kwa wima: shilingi elfu sabini mia nane themanini, jumlisha shilingi elfu kumi na sita mia tisa sabini. Swali namba kumi na moja. Kwa wima: shilingi elfu hamsini na sita mia mbili themanini, jumlisha shilingi elfu thelathini na nane mia mbili sabini. Swali namba kumi na mbili. Kwa wima: shilingi elfu sabini na nane mia nane hamsini, jumlisha shilingi elfu tano mia nane hamsini. Swali namba kumi na tatu. Kwa wima: shilingi elfu tisa mia nane, jumlisha shilingi elfu sitini na tano mia saba. Swali namba kumi na nne. Kwa wima: shilingi elfu arobaini mia tano, jumlisha shilingi elfu thelathini na nane mia tano. Swali namba kumi na tano. Kwa wima: shilingi elfu ishirini na tano mia saba hamsini, jumlisha shilingi elfu hamsini mia mbili hamsini. Swali namba kumi na sita. Kwa wima: shilingi elfu ishirini mia tano hamsini, jumlisha shilingi elfu arobaini na sita mia nne hamsini. Swali namba kumi na saba. Kwa wima: shilingi elfu thelathini na sita mia tisa tisini, jumlisha shilingi elfu ishirini na tatu thelathini. Swali namba kumi na nane. Kwa wima: shilingi elfu hamsini na mbili mia nne, jumlisha shilingi elfu kumi mia nane. Swali namba kumi na tisa. Kwa wima: shilingi elfu sitini na sita mia mbili sabini, jumlisha shilingi elfu tano mia tano. Swali namba ishirini. Kwa wima: shilingi elfu sabini mia saba, jumlisha shilingi elfu kumi na mbili mia tano, jumlisha shilingi elfu moja mia moja hamsini.",
        },
    },
    151: {
        "rate": 0.85,
        "replace": {
            "pg151_n0002": "Mfano.",
            "pg151_n0003": "Mapunda alitumia shilingi elfu arobaini na tano kwa mwezi kununua maziwa,",
            "pg151_n0004": "na shilingi elfu hamsini na mbili mia tano kwa usafiri.",
            "pg151_n0005": "Jumla alitumia kiasi gani cha fedha?",
            "pg151_n0006": "Njia. Panga gharama kwa wima.",
            "pg151_n0007": "Maziwa: shilingi elfu arobaini na tano.",
            "pg151_n0008": "Usafiri: jumlisha shilingi elfu hamsini na mbili mia tano.",
            "pg151_n0009": "Jumla ni shilingi elfu tisini na saba mia tano.",
            "pg151_n0010": "Kwa hiyo, jumla alitumia shilingi elfu tisini na saba mia tano.",
            "pg151_n0011": "Zoezi la Tano.",
            "pg151_n0012": "Jibu maswali yafuatayo.",
            "pg151_n0013": "Swali namba moja. Jeni aliuza pipi kwa shilingi elfu mbili mia tano. Pia alipokea mauzo ya bidhaa shilingi elfu themanini na saba mia tano.",
            "pg151_n0014": "Je, jumla alipata shilingi ngapi?",
            "pg151_n0015": "Swali namba mbili. Muuza mboga alipata noti za shilingi elfu tano, shilingi elfu mbili,",
            "pg151_n0016": "shilingi elfu moja, na sarafu ya shilingi mia mbili baada ya mauzo.",
            "pg151_n0017": "Tafuta jumla ya fedha alizopata.",
            "pg151_n0018": "Swali namba tatu. Mwanafunzi alinunua kitabu cha shilingi elfu tano mia tano na madaftari ya shilingi elfu mbili mia sita.",
            "pg151_n0020": "Je, jumla alitumia kiasi gani cha fedha katika manunuzi yake?",
            "pg151_n0021": "Swali namba nne. Bupe aliuza mchele kwa shilingi elfu thelathini na nane. Pia aliuza maharage kwa shilingi elfu sita.",
            "pg151_n0022": "Je, jumla alipata shilingi ngapi?",
            "pg151_n0023": "Swali namba tano. Mwalimu alimpa Juhudi zawadi ya shilingi elfu moja baada ya kufaulu mtihani wa Hisabati.",
            "pg151_n0024": "Mama yake alimpatia shilingi elfu moja mia saba.",
            "pg151_n0025": "Iwapo Juhudi alikuwa na shilingi mia tatu hamsini mfukoni, jumla alikuwa na kiasi gani cha fedha?",
        },
    },
    152: {
        "rate": 0.85,
        "remove": {"pg152_n0023", "pg152_n0025", "pg152_n0027", "pg152_n0028", "pg152_n0029", "pg152_n0030"},
        "replace": {
            "pg152_n0001": "Swali namba sita. Juma alinunua unga wa mahindi kwa shilingi elfu tisa mia tano,",
            "pg152_n0002": "na njegere kwa shilingi elfu kumi na nne mia saba hamsini.",
            "pg152_n0003": "Je, Juma alitumia jumla ya shilingi ngapi?",
            "pg152_n0004": "Swali namba saba. Mariamu aliuza miche ya miti ya matunda kwa shilingi elfu tano mia tano.",
            "pg152_n0005": "Pia aliuza miche ya miti ya kivuli kwa shilingi elfu nne mia mbili hamsini.",
            "pg152_n0006": "Jumla alipata shilingi ngapi?",
            "pg152_n0007": "Swali namba nane. Wanafunzi walitembelea mbuga ya wanyama ya Ruaha.",
            "pg152_n0008": "Walitumia shilingi elfu arobaini na nane kwa mafuta ya gari na shilingi elfu thelathini mia tano kwa chakula.",
            "pg152_n0010": "Jumla walitumia kiasi gani cha fedha?",
            "pg152_n0011": "Swali namba tisa. Kikundi cha vijana cha Tupendane kilianzisha mradi wa kufuga nyuki.",
            "pg152_n0012": "Walitumia shilingi elfu arobaini na mbili mia nne kuandaa mizinga,",
            "pg152_n0013": "na shilingi elfu arobaini na nane mia mbili kununulia vifaa vya kurina asali.",
            "pg152_n0014": "Walitumia kiasi gani cha fedha kuanzisha mradi huo?",
            "pg152_n0015": "Swali namba kumi. Mwenyekiti wa kijiji alichangisha shilingi elfu thelathini na mbili mia saba hamsini kuwasaidia wazee,",
            "pg152_n0016": "na shilingi elfu sitini mia tatu kwa ajili ya watoto yatima.",
            "pg152_n0018": "Je, mwenyekiti alichangisha jumla ya shilingi ngapi?",
            "pg152_n0021": "Mfano.",
            "pg152_n0022": "Sehemu a. Shilingi elfu arobaini na nane kutoa shilingi elfu tano mia tano hamsini, sawa sawa na shilingi elfu arobaini na mbili mia nne hamsini.",
            "pg152_n0024": "Sehemu b. Shilingi elfu tisini mia tisa kutoa shilingi elfu sabini na tano mia tatu, sawa sawa na shilingi elfu kumi na tano mia sita.",
            "pg152_n0026": "Sehemu c. Hesabu imepangwa kwa wima. Shilingi elfu tisini mia nane, kutoa shilingi elfu thelathini na sita mia tisa hamsini, sawa sawa na shilingi elfu hamsini na tatu mia nane hamsini.",
        },
    },
    153: {
        "rate": 0.85,
        "remove": {"pg153_n0004", "pg153_n0005", "pg153_n0006", "pg153_n0007", "pg153_n0008", "pg153_n0009", "pg153_n0010", "pg153_n0011", "pg153_n0012", "pg153_n0013", "pg153_n0014", "pg153_n0015"},
        "replace": {
            "pg153_n0001": "Zoezi la Sita.",
            "pg153_n0002": "Jibu maswali yafuatayo.",
            "pg153_n0003": "Swali namba moja. Shilingi elfu moja mia saba, kutoa shilingi elfu moja mia mbili, sawa sawa na ngapi? Swali namba mbili. Shilingi elfu tisa mia mbili hamsini, kutoa shilingi elfu mbili mia moja, sawa sawa na ngapi? Swali namba tatu. Shilingi elfu tisini na mbili mia nne hamsini, kutoa shilingi elfu thelathini na nane mia tano kumi. Swali namba nne. Shilingi elfu tisini na tatu mia tano, kutoa shilingi elfu arobaini mia sita hamsini. Swali namba tano. Shilingi elfu sabini na nne, kutoa shilingi elfu thelathini na tano mia sita. Swali namba sita. Shilingi elfu tisini na tisa mia tisa tisini na tisa, kutoa shilingi elfu themanini na sita mia saba. Swali namba saba. Kwa wima: shilingi elfu sabini na mbili mia tatu, kutoa shilingi elfu hamsini na nne mia mbili. Swali namba nane. Kwa wima: shilingi elfu sitini na sita mia tano, kutoa shilingi elfu ishirini na nane mia tisa sabini. Swali namba tisa. Kwa wima: shilingi elfu themanini na tano sitini, kutoa shilingi elfu thelathini na mbili mia saba themanini. Swali namba kumi. Kwa wima: shilingi elfu arobaini na nne mia nne hamsini, kutoa shilingi elfu tatu mia saba hamsini. Swali namba kumi na moja. Kwa wima: shilingi elfu tisini na tisa mia moja, kutoa shilingi elfu sitini na tano mia saba. Swali namba kumi na mbili. Kwa wima: shilingi elfu sabini na sita mia mbili sitini na nane, kutoa shilingi elfu sitini mia tano tisini. Swali namba kumi na tatu. Kwa wima: shilingi elfu sabini na tano mia nane themanini, kutoa shilingi elfu ishirini na tisa mia moja ishirini. Swali namba kumi na nne. Kwa wima: shilingi elfu thelathini mia tano, kutoa shilingi elfu ishirini na tisa mia tisa. Swali namba kumi na tano. Kwa wima: shilingi elfu ishirini na moja mia nane, kutoa shilingi elfu kumi na tano mia tatu hamsini.",
        },
    },
    154: {
        "rate": 0.85,
        "replace": {
            "pg154_n0002": "Mfano.",
            "pg154_n0003": "Anna alikuwa na shilingi elfu themanini mia nane. Alitumia shilingi elfu ishirini kununua sare za shule,",
            "pg154_n0004": "na shilingi elfu kumi na saba mia tano kununua madaftari.",
            "pg154_n0005": "Anna alibakiwa na kiasi gani cha fedha?",
            "pg154_n0006": "Njia.",
            "pg154_n0007": "Hatua ya kwanza. Jumlisha kiasi alichotumia.",
            "pg154_n0008": "Sare: shilingi elfu ishirini.",
            "pg154_n0009": "Madaftari: jumlisha shilingi elfu kumi na saba mia tano.",
            "pg154_n0010": "Jumla ni shilingi elfu thelathini na saba mia tano.",
            "pg154_n0011": "Anna alitumia jumla ya shilingi elfu thelathini na saba mia tano kununulia sare za shule na madaftari.",
            "pg154_n0013": "Hatua ya pili. Chukua kiasi alichokuwa nacho, kisha toa kiasi alichotumia.",
            "pg154_n0014": "Kiasi alichokuwa nacho: shilingi elfu themanini mia nane.",
            "pg154_n0015": "Toa jumla aliyotumia: shilingi elfu thelathini na saba mia tano.",
            "pg154_n0016": "Jibu ni shilingi elfu arobaini na tatu mia tatu.",
            "pg154_n0017": "Kwa hiyo, Anna alibakiwa na shilingi elfu arobaini na tatu mia tatu.",
            "pg154_n0018": "Zoezi la Saba.",
            "pg154_n0019": "Jibu maswali yafuatayo.",
            "pg154_n0020": "Swali namba moja. Paulo analipwa shilingi elfu sitini kwa mwezi.",
            "pg154_n0021": "Anatumia shilingi elfu thelathini na saba mia nne na zinazobaki anaweka akiba.",
            "pg154_n0022": "Je, Paulo anaweka akiba kiasi gani?",
        },
    },
    155: {
        "rate": 0.85,
        "replace": {
            "pg155_n0001": "Swali namba mbili. Pendo alikuwa na shilingi elfu tisini. Alinunua mashuka mawili kwa shilingi elfu thelathini na mbili mia tano,",
            "pg155_n0002": "na gauni kwa shilingi elfu arobaini.",
            "pg155_n0003": "Alibakiwa na shilingi ngapi?",
            "pg155_n0004": "Swali namba tatu. Safina alipewa shilingi elfu moja kwa matumizi ya shule.",
            "pg155_n0005": "Alinunua maji ya shilingi mia nne hamsini na chapati za shilingi mia tatu.",
            "pg155_n0006": "Safina alibakiwa na shilingi ngapi?",
            "pg155_n0007": "Swali namba nne. Musa alipata faida ya shilingi elfu mbili sabini baada ya kuuza mahindi kwa shilingi elfu tisini na saba mia sita hamsini.",
            "pg155_n0009": "Alikuwa amenunua mahindi hayo kwa shilingi ngapi?",
            "pg155_n0010": "Swali namba tano. Salum alichukua shilingi elfu themanini na tano katika akiba yake iliyoko benki.",
            "pg155_n0011": "Akalipia umeme wa shilingi elfu hamsini mia nne hamsini na maji shilingi elfu kumi na tano.",
            "pg155_n0012": "Salum alibakiza kiasi gani cha fedha?",
            "pg155_n0013": "Swali namba sita. Bwana Fungafunga alinunua mbuzi kwa shilingi elfu thelathini,",
            "pg155_n0014": "na kuku mmoja kwa shilingi elfu kumi na moja mia tano.",
            "pg155_n0015": "Iwapo alikuwa na shilingi elfu sabini, alibakiwa na kiasi gani cha fedha?",
            "pg155_n0016": "Swali namba saba. Furaha ana shilingi elfu kumi. Aliwapatia watoto wake wawili fedha hiyo kwa ajili ya nauli.",
            "pg155_n0017": "Iwapo alimpatia mmoja shilingi elfu nne mia sita,",
            "pg155_n0018": "wa pili alimpatia shilingi ngapi?",
            "pg155_n0019": "Swali namba nane. Mfanyabiashara ana shilingi elfu saba mia tano.",
            "pg155_n0020": "Anahitaji kiasi gani zaidi ili kununua kreti ya chupa ishirini na nne za soda,",
            "pg155_n0021": "iwapo kila chupa huuzwa shilingi mia tano?",
            "pg155_n0022": "Swali namba tisa. Mwalimu mkuu alinunua kitabu kwa shilingi elfu sita mia tano.",
            "pg155_n0023": "Pia alinunua madaftari kumi kwa shilingi mia mbili hamsini kila moja.",
            "pg155_n0024": "Alimpatia muuzaji noti ya shilingi elfu kumi. Alirudishiwa kiasi gani cha fedha?",
            "pg155_n0026": "Swali namba kumi. Nasibu alitoa noti ya shilingi elfu kumi kulipia nauli ya shilingi elfu sita mia tano.",
            "pg155_n0027": "Alirudishiwa kiasi gani cha fedha?",
        },
    },
    156: {
        "rate": 0.85,
        "remove": {"pg156_n0005", "pg156_n0006", "pg156_n0007", "pg156_n0011", "pg156_n0012", "pg156_n0013", "pg156_n0014", "pg156_n0015", "pg156_n0016", "pg156_n0017", "pg156_n0018"},
        "replace": {
            "pg156_n0003": "Mfano.",
            "pg156_n0004": "Mfano wa kwanza. Shilingi mia saba hamsini kuzidisha nne, sawa sawa na shilingi elfu tatu. Mfano wa pili. Kwa wima: shilingi mia sita hamsini kuzidisha saba, sawa sawa na shilingi elfu nne mia tano hamsini.",
            "pg156_n0008": "Zoezi la Nane.",
            "pg156_n0009": "Jibu maswali yafuatayo.",
            "pg156_n0010": "Swali namba moja. Shilingi mia moja sitini kuzidisha sita. Swali namba mbili. Shilingi mia tisa sitini kuzidisha thelathini na sita. Swali namba tatu. Shilingi mia sita na tano kuzidisha kumi na sita. Swali namba nne. Shilingi themanini na saba kuzidisha kumi na tano. Swali namba tano. Shilingi mia tatu kuzidisha kumi na tano. Swali namba sita. Shilingi mia tisa hamsini kuzidisha tisa. Swali namba saba. Kwa wima: shilingi mia tisa hamsini kuzidisha saba. Swali namba nane. Kwa wima: shilingi sabini na tano kuzidisha kumi na tatu. Swali namba tisa. Kwa wima: shilingi mia tano sitini kuzidisha kumi na mbili. Swali namba kumi. Kwa wima: shilingi mia moja na tano kuzidisha themanini. Swali namba kumi na moja. Kwa wima: shilingi mia mbili kuzidisha ishirini na tano. Swali namba kumi na mbili. Kwa wima: shilingi mia tisa sitini kuzidisha kumi na nne.",
        },
    },
    157: {
        "rate": 0.85,
        "remove": {"pg157_n0007", "pg157_n0008", "pg157_n0009", "pg157_n0010", "pg157_n0011"},
        "replace": {
            "pg157_n0002": "Mfano.",
            "pg157_n0003": "Pakiti ya majani ya chai inauzwa kwa shilingi mia tano.",
            "pg157_n0004": "Tafuta gharama ya kununua pakiti kumi na mbili za majani ya chai ya aina hiyo.",
            "pg157_n0006": "Njia. Panga shilingi mia tano kuzidisha kumi na mbili kwa wima. Kwanza, mia tano kuzidisha mbili, sawa sawa na elfu moja. Pili, mia tano kuzidisha kumi, sawa sawa na elfu tano. Jumlisha elfu moja na elfu tano, sawa sawa na shilingi elfu sita.",
            "pg157_n0012": "Kwa hiyo, gharama ya kununua pakiti kumi na mbili za majani ya chai ni shilingi elfu sita.",
            "pg157_n0014": "Zoezi la Tisa.",
            "pg157_n0015": "Jibu maswali yafuatayo.",
            "pg157_n0016": "Swali namba moja. Kalamu moja inauzwa shilingi mia mbili hamsini.",
            "pg157_n0017": "Kalamu kumi na tatu za aina hiyo zitauzwa shilingi ngapi?",
            "pg157_n0018": "Swali namba mbili. Machinga aliuza sahani arobaini.",
            "pg157_n0019": "Iwapo sahani moja iliuzwa kwa shilingi mia sita hamsini, alipata jumla ya kiasi gani cha fedha?",
            "pg157_n0021": "Swali namba tatu. Bei ya tikitimaji ni shilingi mia nane hamsini.",
            "pg157_n0022": "Amina atahitaji kiasi gani cha fedha kununua matikitimaji kumi?",
            "pg157_n0023": "Swali namba nne. Fungu la nyanya huuzwa kwa shilingi mia saba ishirini.",
            "pg157_n0024": "Mafungu hamsini ya nyanya ya aina hiyo yatauzwa kwa shilingi ngapi?",
        },
    },
    158: {
        "rate": 0.85,
        "replace": {
            "pg158_n0001": "Swali namba tano. Mfanyabiashara alinunua mikate hamsini kwa shilingi mia tisa hamsini kila mmoja.",
            "pg158_n0002": "Aliamua kuiuza kwa shilingi mia nane kila mmoja.",
            "pg158_n0003": "Je, alipata hasara kiasi gani?",
            "pg158_n0004": "Swali namba sita. Kabibi aliuza maembe ishirini kwa shilingi mia tano kila moja.",
            "pg158_n0005": "Je, Kabibi alipata kiasi gani cha fedha?",
            "pg158_n0006": "Swali namba saba. Dereva wa teksi alimtoza abiria wake shilingi mia tisa hamsini kwa kila kilomita.",
            "pg158_n0007": "Atalipwa shilingi ngapi kwa umbali wa kilomita ishirini na saba?",
            "pg158_n0009": "Swali namba nane. Shule ya Msingi Azimio hulipia bili ya umeme ya shilingi elfu thelathini na sita mia tano kwa mwezi.",
            "pg158_n0010": "Shule italipia kiasi gani kwa miezi miwili?",
            "pg158_n0012": "Swali namba tisa. Zuwena hupata shilingi mia saba hamsini kila siku baada ya kuuza barafu.",
            "pg158_n0013": "Je, alipata kiasi gani cha fedha kwa wiki?",
            "pg158_n0014": "Swali namba kumi. Basi lina abiria thelathini na mbili.",
            "pg158_n0015": "Iwapo nauli ya abiria mmoja ni shilingi mia nne hamsini, kiasi gani cha fedha kitakusanywa kutoka kwa abiria wote?",
            "pg158_n0017": "Jikumbushe.",
            "pg158_n0018": "Jambo la kwanza. Tunajumlisha na kutoa fedha kwa fedha.",
            "pg158_n0019": "Jambo la pili. Tunazidisha fedha kwa namba.",
        },
    },
    159: {
        "rate": 0.85,
        "replace": {
            "pg159_n0001": "Sura ya Kumi na Mbili.",
            "pg159_n0012": "Zoezi la Kwanza: Marudio.",
            "pg159_n0013": "Chunguza maumbo yafuatayo, kisha jibu swali namba moja hadi saba.",
            "pg159_n0014": "Maelezo ya maumbo. Umbo a ni mraba. Umbo b ni pembetatu. Umbo c ni mstatili. Umbo d ni duara.",
            "pg159_n0015": "Umbo e lina pande nne, huku upande mmoja ukiwa umepinda kwa mwelekeo. Umbo f ni umbo lisilo la kawaida lenye sehemu nyembamba upande wa kushoto. Umbo g ni pembetatu.",
            "pg159_n0016": "Umbo h ni duara. Umbo i ni msambamba wenye pande nne. Umbo j ni pentagoni yenye pande tano. Umbo k ni mstatili mwembamba uliosimama.",
        },
    },
    160: {
        "rate": 0.85,
        "replace": {
            "pg160_n0001": "Swali namba moja. Maumbo yapi ni ya pembe nne?",
            "pg160_n0002": "Swali namba mbili. Maumbo yapi ni duara?",
            "pg160_n0003": "Swali namba tatu. Andika majina ya maumbo a hadi d.",
            "pg160_n0004": "Swali namba nne. Umbo a na b, kila moja lina pembe ngapi?",
            "pg160_n0005": "Swali namba tano. Maumbo yapi hayana pembe?",
            "pg160_n0006": "Swali namba sita. Maumbo yapi yana pembetatu?",
            "pg160_n0007": "Swali namba saba. Taja tofauti ya maumbo bapa na yasiyo bapa.",
            "pg160_n0010": "Michoro ifuatayo inaonesha maumbo bapa na majina yake.",
            "pg160_n0012": "Mstari wa kwanza, kutoka kushoto kwenda kulia: pembetatu yenye pande tatu; mraba wenye pande nne zinazolingana; na mstatili wenye pande nne, pande zinazoelekeana zikilingana.",
            "pg160_n0013": "Mstari wa pili: duara lisilo na pembe; pentagoni yenye pande tano; na heksagoni yenye pande sita.",
        },
    },
    161: {
        "rate": 0.85,
        "remove": {"pg161_n0005", "pg161_n0006", "pg161_n0007", "pg161_n0008"},
        "replace": {
            "pg161_n0002": "Zoezi la Pili.",
            "pg161_n0003": "Tazama maumbo bapa a hadi j, kisha jibu maswali yanayofuata.",
        },
        "after": {
            "pg161_n0004": [
                "Maumbo yamepangwa kwa herufi a hadi j. Umbo a lina pande nne na sehemu moja inayoingia ndani. Umbo b lina umbo la mshale unaoelekea juu na lina pande saba. Umbo c lina pande sita na sehemu moja inayoingia ndani.",
                "Umbo d ni pembe nne lenye pande mbili zilizo sambamba. Umbo e ni pembetatu. Umbo f ni pembe tano. Umbo g ni duara. Umbo h ni umbo lisilo la kawaida lenye kingo zilizopinda. Umbo i ni duara. Umbo j ni mstatili.",
            ],
        },
    },
    162: {
        "rate": 0.85,
        "remove": {"pg162_n0010", "pg162_n0011", "pg162_n0012"},
        "replace": {
            "pg162_n0001": "Swali namba moja. Chora maumbo bapa yenye pembe nne.",
            "pg162_n0002": "Swali namba mbili. Maumbo ya pembetatu yapo mangapi?",
            "pg162_n0003": "Swali namba tatu. Chora maumbo ya duara.",
            "pg162_n0004": "Swali namba nne. Chora maumbo bapa yenye pembe zaidi ya nne.",
            "pg162_n0005": "Swali namba tano. Tengeneza maumbo bapa b, d, e, f, i na j kwa kutumia karatasi.",
            "pg162_n0009": "Chunguza maumbo a hadi h. Maelezo ya mchoro yanafuata.",
        },
        "after": {
            "pg162_n0009": [
                "Mchoro una vitu vinane vilivyowekwa herufi a hadi h. Umbo a ni kasha la mchemraba. Umbo b ni gogo lenye umbo la silinda. Umbo c ni msambamba. Umbo d ni chupa. Umbo e ni msambamba wenye pande zote sawa. Umbo f ni pembetatu. Umbo g ni kasha la mstatili lililo wazi. Umbo h ni kitabu.",
            ],
        },
    },
    163: {
        "rate": 0.85,
        "remove": {"pg163_n0003", "pg163_n0004", "pg163_n0005", "pg163_n0006", "pg163_n0007"},
        "replace": {
            "pg163_n0001": "Mifano mbalimbali ya maumbo yasiyo bapa imeoneshwa katika michoro ya vitu a hadi f.",
            "pg163_n0008": "Zoezi la Tatu.",
            "pg163_n0009": "Jibu maswali yafuatayo.",
            "pg163_n0010": "Swali namba moja. Chora maumbo matano yasiyo bapa.",
            "pg163_n0011": "Swali namba mbili. Tengeneza maumbo matano yasiyo bapa kwa kutumia vifaa halisi vinavyopatikana katika mazingira yako.",
            "pg163_n0015": "Kazi namba moja.",
            "pg163_n0016": "Hatua ya kwanza. Tengeneza maumbo bapa na yasiyo bapa.",
            "pg163_n0017": "Hatua ya pili. Unganisha maumbo hayo ili kupata pambo.",
            "pg163_n0018": "Hatua ya tatu. Tengeneza pambo kwa kutumia maumbo ya aina moja.",
            "pg163_n0019": "Hatua ya nne. Tengeneza pambo kwa kutumia maumbo bapa na yasiyo bapa.",
        },
        "after": {
            "pg163_n0002": [
                "Mchoro a ni pipa lenye umbo la silinda. Mchoro b ni pia lenye umbo la koni. Mchoro c ni kasha lenye umbo la mche mstatili. Mchoro d ni yai lenye umbo la mviringo. Mchoro e ni mpira wenye umbo la tufe. Mchoro f ni bilauri yenye sehemu pana juu na nyembamba chini.",
            ],
        },
    },
    164: {
        "rate": 0.85,
        "remove": {"pg164_n0006", "pg164_n0007"},
        "replace": {
            "pg164_n0001": "Mfano. Picha inaonesha mapambo mawili yaliyotengenezwa kwa maumbo. Upande wa kushoto kuna pazia lenye mistari ya mioyo midogo; upande wa kulia kuna mkufu wa duara za rangi mbili na pambo la mviringo chini.",
            "pg164_n0002": "Zoezi la Nne.",
            "pg164_n0003": "Jibu maswali yafuatayo.",
            "pg164_n0004": "Swali namba moja. Angalia na ubaini majina ya maumbo a, b, c na d, kisha jibu maswali yanayofuata.",
        },
        "after": {
            "pg164_n0005": [
                "Umbo a ni mraba. Umbo b ni pembetatu. Umbo c ni duara. Umbo d ni mstatili.",
            ],
        },
    },
    165: {
        "rate": 0.85,
        "replace": {
            "pg165_n0001": "Roman moja. Umbo a ni umbo gani? Andika jibu kwenye nafasi iliyo wazi.",
            "pg165_n0002": "Roman mbili. Umbo b ni umbo gani? Andika jibu kwenye nafasi iliyo wazi.",
            "pg165_n0003": "Roman tatu. Umbo c ni umbo gani? Andika jibu kwenye nafasi iliyo wazi.",
            "pg165_n0004": "Roman nne. Umbo d ni umbo gani? Andika jibu kwenye nafasi iliyo wazi.",
            "pg165_n0005": "Swali namba mbili. Umbo la pembetatu lina pembe ngapi?",
            "pg165_n0006": "Swali namba tatu. Taja maumbo mawili bapa.",
            "pg165_n0007": "Swali namba nne. Taja vitu viwili ambavyo vina maumbo yasiyo bapa vinavyopatikana katika mazingira yako.",
            "pg165_n0009": "Swali namba tano. Chora mapambo matatu tofauti kwa kutumia maumbo bapa.",
            "pg165_n0011": "Swali namba sita. Chora mapambo matatu tofauti kwa kutumia maumbo yasiyo bapa.",
            "pg165_n0015": "Kazi namba mbili.",
            "pg165_n0017": "Hatua.",
            "pg165_n0018": "Hatua ya kwanza. Weka rula kwenye karatasi na uchague alama ya kuanzia na ya kumalizia.",
            "pg165_n0019": "Kwa mfano, sentimita sifuri iwe mwanzo na sentimita saba iwe mwisho.",
            "pg165_n0021": "Hatua ya pili. Chora mstari kwa penseli kuanzia alama ya sentimita sifuri hadi alama ya sentimita saba.",
            "pg165_n0023": "Hatua ya tatu. Weka mikato midogo kwenye mstari katika alama za mwanzo na mwisho.",
            "pg165_n0025": "Hatua ya nne. Toa rula, kisha weka herufi kubwa mbili tofauti juu ya mikato yote miwili, kama herufi A na B, X na Y, au C na D.",
            "pg165_n0027": "Hatua ya tano. Andika jina la kipande hicho cha mstari kutoka herufi A hadi herufi B.",
            "pg165_n0028": "Hatua ya sita. Kwa kifupi, kipande hicho huandikwa A B, X Y, au C D, kikiwa na mstari mfupi juu ya herufi mbili.",
        },
    },
    166: {
        "rate": 0.85,
        "remove": {"pg166_n0005", "pg166_n0006", "pg166_n0007", "pg166_n0013", "pg166_n0016", "pg166_n0017"},
        "replace": {
            "pg166_n0001": "Mfano. Picha ya vifaa ina penseli, karatasi na rula.",
            "pg166_n0002": "Chora kipande cha mstari chenye urefu wa sentimita sita na uandike jina lake.",
            "pg166_n0004": "Jibu. Mchoro una kipande cha mstari cha sentimita sita. Ncha ya kushoto imeandikwa herufi A, na ncha ya kulia herufi B. Jina lake ni kipande cha mstari A B.",
            "pg166_n0009": "Kazi namba tatu.",
            "pg166_n0010": "Chora mwale.",
            "pg166_n0011": "Hatua.",
            "pg166_n0012": "Hatua ya kwanza. Tumia rula kuchora kipande cha mstari kutoka herufi A hadi herufi B. Mstari una ncha mbili.",
            "pg166_n0014": "Hatua ya pili. Endeleza kipande hicho upande mmoja, kushoto au kulia, kisha uweke mshale.",
            "pg166_n0015": "Mchoro wa kwanza unaanzia A, unapita B, na mshale unaelekea kulia. Mchoro wa pili unaanzia B, unapita A, na mshale unaelekea kushoto.",
        },
    },
    167: {
        "rate": 0.85,
        "remove": {"pg167_n0002", "pg167_n0025", "pg167_n0026", "pg167_n0027", "pg167_n0028"},
        "replace": {
            "pg167_n0001": "Kuna miale miwili: mwale A B na mwale B A.",
            "pg167_n0003": "Mwale A B huandikwa kwa herufi A B zikiwa na mshale juu unaoelekea B. Mwale B A huandikwa kwa herufi B A zikiwa na mshale juu unaoelekea A.",
            "pg167_n0004": "Alama ya mshale inawakilisha mwale. Anza kusoma kwa herufi iliyo kwenye sehemu mwale unapoanzia.",
            "pg167_n0008": "Zoezi la Tano.",
            "pg167_n0009": "Chora vipande vya mistari vyenye urefu unaooneshwa katika jedwali.",
            "pg167_n0010": "Jedwali lina safu mbili: namba, na kipande cha mstari.",
            "pg167_n0011": "Mstari wa kwanza. Kipande cha mstari P Q, sawa sawa na sentimita nne.",
            "pg167_n0012": "Mstari wa pili. Kipande cha mstari C D, sawa sawa na sentimita tano.",
            "pg167_n0013": "Mstari wa tatu. Kipande cha mstari L M, sawa sawa na sentimita sita.",
            "pg167_n0014": "Mstari wa nne. Kipande cha mstari J K, sawa sawa na sentimita saba.",
            "pg167_n0015": "Mstari wa tano. Kipande cha mstari X Y, sawa sawa na sentimita nane.",
            "pg167_n0016": "Mstari wa sita. Kipande cha mstari E F, sawa sawa na sentimita tisa.",
            "pg167_n0017": "Mstari wa saba. Kipande cha mstari M N, sawa sawa na sentimita kumi.",
            "pg167_n0019": "Kazi namba nne.",
            "pg167_n0021": "Hatua.",
            "pg167_n0022": "Hatua ya kwanza. Tumia rula kuchora miale miwili: mmoja uelekee kushoto na mwingine uelekee kulia. Kila mwale unaanzia kwenye ncha yenye herufi, kisha mshale unaonesha mwelekeo wake.",
            "pg167_n0024": "Hatua ya pili. Unganisha miale hiyo miwili kupata mstari ulionyooka. Mstari una mishale kwenye ncha zote mbili kuonesha unaendelea pande zote.",
        },
    },
    168: {
        "rate": 0.85,
        "replace": {
            "pg168_n0001": "Hatua ya tatu. Miale miwili imeunda mstari mnyoofu A B, au B A.",
            "pg168_n0002": "Hatua ya nne. Kwa kifupi, mstari mnyoofu huandikwa A B au B A, ukiwa na mshale unaoelekea pande mbili juu ya herufi.",
            "pg168_n0003": "Alama ya mshale wenye ncha mbili inawakilisha mstari mnyoofu.",
            "pg168_n0004": "Zoezi la Sita.",
            "pg168_n0005": "Jibu maswali yafuatayo.",
            "pg168_n0006": "Swali namba moja. Chora vipande viwili vya mstari vinavyolingana.",
            "pg168_n0007": "Swali namba mbili. Chora mistari minyoofu mitatu, kisha taja majina yake.",
            "pg168_n0009": "Swali namba tatu. Andika tofauti kati ya kipande cha mstari na mstari mnyoofu.",
            "pg168_n0011": "Swali namba nne. Je, unaweza kuchora mstari mnyoofu bila rula?",
            "pg168_n0012": "Swali namba tano. Je, unaweza kuchora kipande cha mstari cha sentimita nne bila rula?",
            "pg168_n0013": "Kwa nini?",
            "pg168_n0014": "Swali namba sita. Chora mwale X Y na mwale Y X.",
            "pg168_n0015": "Swali namba saba. Andika tofauti kati ya kipande cha mstari na mwale.",
            "pg168_n0016": "Swali namba nane. Urefu wa kipande cha mstari unapimwa kwa kutumia kifaa gani?",
            "pg168_n0018": "Swali namba tisa. Chora kipande cha mstari P Q. Je, kipande hiki kina ncha ngapi?",
            "pg168_n0020": "Swali namba kumi. Unganisha miisho ya vipande vitatu vya mstari A B, B C na C A.",
            "pg168_n0021": "Andika jina la umbo ulilopata.",
        },
    },
    169: {
        "rate": 0.85,
        "replace": {
            "pg169_n0003": "Kazi namba tano.",
            "pg169_n0005": "Mchoro unaonesha mstatili. Pande zake za juu na chini ni urefu; pande zake za kushoto na kulia ni upana.",
            "pg169_n0006": "Kupima mzingo kunamaanisha kupima urefu wa kuzunguka pande zote za umbo.",
            "pg169_n0007": "Hatua za kupima mzingo.",
            "pg169_n0008": "Hatua ya kwanza. Kabla ya kuweka kipimio, hakikisha unaanzia alama ya sifuri au mwanzo wa kipimo.",
            "pg169_n0010": "Hatua ya pili. Zungushia futikamba au uzi kwenye umbo bila kuacha nafasi, kisha weka alama kwenye makutano.",
            "pg169_n0012": "Hatua ya tatu. Ikiwa umetumia futikamba, soma urefu kwenye alama.",
            "pg169_n0013": "Hatua ya nne. Ikiwa umetumia uzi, ukunjue na kuulaza kwenye rula,",
            "pg169_n0014": "kisha usome urefu kwenye alama ya mwisho inayolingana na mwisho wa uzi.",
            "pg169_n0016": "Hatua ya tano. Kwa umbo bapa lenye pande, pima urefu wa pande zote.",
            "pg169_n0017": "Tumia rula au futikamba, kisha jumlisha urefu wa pande zote.",
            "pg169_n0019": "Hatua ya sita. Je, umepata urefu gani wa mzunguko?",
        },
    },
    170: {
        "rate": 0.85,
        "remove": {"pg170_n0005", "pg170_n0006", "pg170_n0007"},
        "replace": {
            "pg170_n0001": "Sehemu a. Mzingo wa mstatili.",
            "pg170_n0002": "Mfano.",
            "pg170_n0003": "Tafuta mzingo wa mstatili ufuatao.",
            "pg170_n0004": "Mchoro ni mstatili. Upande wa juu na wa chini kila mmoja una urefu wa sentimita mia moja. Upande wa kushoto na wa kulia kila mmoja una upana wa sentimita arobaini.",
            "pg170_n0009": "Mzingo wa mstatili sawa sawa na urefu jumlisha upana jumlisha urefu jumlisha upana.",
            "pg170_n0010": "Mzingo wa mstatili sawa sawa na sentimita mia moja jumlisha sentimita arobaini jumlisha sentimita mia moja jumlisha sentimita arobaini.",
            "pg170_n0011": "Sawa sawa na sentimita mia mbili themanini.",
            "pg170_n0012": "Njia mbadala.",
            "pg170_n0013": "Mstatili una pande mbili zinazolingana kwa urefu, na pande mbili zinazolingana kwa upana.",
            "pg170_n0015": "Mzingo wa mstatili sawa sawa na urefu kuzidisha mbili, jumlisha upana kuzidisha mbili.",
            "pg170_n0016": "Mzingo wa mstatili sawa sawa na sentimita mia moja kuzidisha mbili, jumlisha sentimita arobaini kuzidisha mbili.",
            "pg170_n0017": "Sawa sawa na sentimita mia mbili jumlisha sentimita themanini.",
            "pg170_n0018": "Sawa sawa na sentimita mia mbili themanini.",
            "pg170_n0019": "Kwa hiyo, mzingo wa mstatili ni sentimita mia mbili themanini.",
            "pg170_n0020": "Sehemu b. Mzingo wa mraba.",
            "pg170_n0021": "Mfano.",
            "pg170_n0022": "Tafuta mzingo wa mraba ufuatao.",
            "pg170_n0023": "Mchoro ni mraba. Kila upande una urefu wa sentimita ishirini.",
        },
    },
    171: {
        "rate": 0.85,
        "replace": {
            "pg171_n0001": "Njia.",
            "pg171_n0002": "Mzingo wa mraba sawa sawa na upande jumlisha upande jumlisha upande jumlisha upande.",
            "pg171_n0003": "Mzingo wa mraba sawa sawa na sentimita ishirini jumlisha sentimita ishirini jumlisha sentimita ishirini jumlisha sentimita ishirini.",
            "pg171_n0004": "Sawa sawa na sentimita themanini.",
            "pg171_n0006": "Mraba una pande nne zinazolingana.",
            "pg171_n0007": "Mzingo wa mraba sawa sawa na upande mmoja kuzidisha nne.",
            "pg171_n0008": "Mzingo wa mraba sawa sawa na sentimita ishirini kuzidisha nne.",
            "pg171_n0009": "Sawa sawa na sentimita themanini.",
            "pg171_n0010": "Kwa hiyo, mzingo wa mraba ni sentimita themanini.",
            "pg171_n0011": "Sehemu c. Mzingo wa pembetatu.",
            "pg171_n0013": "Tafuta mzingo wa pembetatu ifuatayo.",
            "pg171_n0014": "Mchoro ni pembetatu. Pande zake zina urefu wa sentimita sita, sentimita saba na sentimita tisa.",
            "pg171_n0015": "Tumia urefu wa pande zote tatu.",
            "pg171_n0016": "Anza na upande wa sentimita sita, kisha sentimita saba, kisha sentimita tisa.",
            "pg171_n0018": "Mzingo wa pembetatu sawa sawa na upande jumlisha upande jumlisha upande.",
            "pg171_n0019": "Mzingo wa pembetatu sawa sawa na sentimita sita jumlisha sentimita saba jumlisha sentimita tisa.",
            "pg171_n0020": "Sawa sawa na sentimita ishirini na mbili.",
            "pg171_n0021": "Kwa hiyo, mzingo wa pembetatu ni sentimita ishirini na mbili.",
        },
    },
    173: {
        "rate": 0.85,
        "remove": {"pg173_n0002", "pg173_n0003", "pg173_n0004", "pg173_n0010", "pg173_n0011", "pg173_n0012", "pg173_n0013"},
        "replace": {
            "pg173_n0001": "Mwendelezo wa Zoezi la Saba. Umbo namba tisa ni pembetatu yenye pande tatu, kila upande ukiwa mita thelathini. Umbo namba kumi ni mraba; kila upande una urefu wa mita kumi na sita.",
            "pg173_n0006": "Mfano wa Kwanza.",
            "pg173_n0007": "Bustani ya maua ina umbo la mraba kama lilivyooneshwa kwenye mchoro.",
            "pg173_n0008": "Kila upande wake ni mita ishirini na tano. Tafuta mzingo wake.",
            "pg173_n0014": "Njia. Mzingo wa mraba, sawa sawa na upande jumlisha upande jumlisha upande jumlisha upande.",
            "pg173_n0015": "Mita ishirini na tano jumlisha mita ishirini na tano jumlisha mita ishirini na tano jumlisha mita ishirini na tano,",
            "pg173_n0016": "sawa sawa na mita mia moja.",
            "pg173_n0017": "Njia mbadala.",
            "pg173_n0018": "Mzingo wa mraba, sawa sawa na upande mmoja kuzidisha nne.",
            "pg173_n0019": "Mita ishirini na tano kuzidisha nne, sawa sawa na mita mia moja.",
            "pg173_n0021": "Kwa hiyo, mzingo wa bustani ni mita mia moja.",
        },
    },
    174: {
        "rate": 0.85,
        "remove": {"pg174_n0005", "pg174_n0006", "pg174_n0007"},
        "replace": {
            "pg174_n0001": "Mfano wa Pili.",
            "pg174_n0002": "Mariamu alichora mstatili wenye urefu wa sentimita kumi na upana wa sentimita tano.",
            "pg174_n0003": "Tafuta mzingo wake.",
            "pg174_n0004": "Njia. Mchoro ni mstatili. Pande za juu na chini zina sentimita kumi kila moja. Pande za kushoto na kulia zina sentimita tano kila moja.",
            "pg174_n0008": "Mzingo wa mstatili, sawa sawa na urefu jumlisha upana jumlisha urefu jumlisha upana.",
            "pg174_n0009": "Sentimita kumi jumlisha sentimita tano jumlisha sentimita kumi jumlisha sentimita tano,",
            "pg174_n0010": "sawa sawa na sentimita thelathini.",
            "pg174_n0011": "Njia mbadala.",
            "pg174_n0012": "Mzingo wa mstatili, sawa sawa na urefu kuzidisha mbili, jumlisha upana kuzidisha mbili.",
            "pg174_n0013": "Sentimita kumi kuzidisha mbili, jumlisha sentimita tano kuzidisha mbili,",
            "pg174_n0014": "sawa sawa na sentimita ishirini jumlisha sentimita kumi,",
            "pg174_n0015": "sawa sawa na sentimita thelathini.",
            "pg174_n0016": "Kwa hiyo, mzingo wa mstatili ni sentimita thelathini.",
            "pg174_n0017": "Mfano wa Tatu.",
            "pg174_n0018": "Ashura alitembea kilomita tatu kutoka nyumbani hadi shuleni.",
            "pg174_n0020": "Umbali wa kutoka shuleni hadi sokoni ni kilomita mbili, kwa njia tofauti na ile ya nyumbani.",
            "pg174_n0022": "Baada ya kununua matunda, alipita njia ya mkato ya kilomita moja kufika nyumbani.",
            "pg174_n0023": "Je, Ashura alitembea umbali gani katika safari yake yote?",
        },
    },
    175: {
        "rate": 0.85,
        "remove": {"pg175_n0002", "pg175_n0003", "pg175_n0004", "pg175_n0005", "pg175_n0024", "pg175_n0025", "pg175_n0026", "pg175_n0027", "pg175_n0028", "pg175_n0029"},
        "replace": {
            "pg175_n0001": "Njia. Maelezo ya mchoro. Njia tatu zinaunda pembetatu ya safari: kutoka nyumbani hadi shuleni ni kilomita tatu; kutoka shuleni hadi sokoni ni kilomita mbili; na kutoka sokoni hadi nyumbani ni kilomita moja.",
            "pg175_n0006": "Umbali wote, sawa sawa na umbali kutoka nyumbani hadi shuleni, jumlisha umbali kutoka shuleni hadi sokoni,",
            "pg175_n0007": "jumlisha umbali kutoka sokoni hadi nyumbani.",
            "pg175_n0009": "Kilomita tatu jumlisha kilomita mbili jumlisha kilomita moja, sawa sawa na kilomita sita.",
            "pg175_n0011": "Kwa hiyo, Ashura alitembea kilomita sita katika safari yake yote.",
            "pg175_n0013": "Zoezi la Nane.",
            "pg175_n0014": "Jibu maswali yafuatayo.",
            "pg175_n0015": "Swali namba moja. Urefu wa upande mmoja wa mraba ni sentimita ishirini na tatu. Tafuta mzingo wa mraba.",
            "pg175_n0017": "Swali namba mbili. Mzingo wa mstatili ni sentimita themanini. Tafuta upana ikiwa urefu ni sentimita thelathini.",
            "pg175_n0019": "Swali namba tatu. Bustani ya shule ni mstatili. Urefu ni sentimita elfu kumi na mbili na upana ni sentimita mia nane.",
            "pg175_n0021": "Tafuta mzingo wa bustani hiyo.",
            "pg175_n0022": "Swali namba nne. Tafuta mzingo wa pembetatu iwapo kila upande ni sentimita kumi na saba.",
            "pg175_n0023": "Swali namba tano. Tafuta mzingo wa mraba iwapo kila upande ni mita kumi na sita.",
        },
    },
    176: {
        "rate": 0.85,
        "replace": {
            "pg176_n0001": "Swali namba sita. Tafuta urefu wa waya uliotumika kuzungushia dirisha lenye urefu wa mita tatu na upana wa mita mbili.",
            "pg176_n0003": "Swali namba saba. Je, inawezekana mzingo wa mstatili kulingana na mzingo wa mraba? Toa mfano.",
            "pg176_n0005": "Swali namba nane. Chora maumbo mawili tofauti yenye mzingo wa sentimita kumi na mbili kila moja.",
            "pg176_n0007": "Swali namba tisa. Mzingo wa mraba A ni mita nne. Miraba miwili ya mraba A inaunganishwa kuunda mstatili B.",
            "pg176_n0008": "Mchoro unaonesha mraba A mmoja na mstatili B ulioundwa kwa miraba miwili inayolingana, iliyounganishwa ubavu kwa ubavu.",
            "pg176_n0009": "Baraka alipata mzingo wa mstatili B kuwa mita nane; Neema alipata mita sita.",
            "pg176_n0010": "Nani alipata jibu sahihi? Toa sababu.",
            "pg176_n0012": "Swali namba kumi. Mwanafunzi alipewa waya wa mita ishirini na nane na kuzungushia banda la kuku.",
            "pg176_n0014": "Iwapo urefu wa banda ni mita kumi, tafuta upana wake.",
            "pg176_n0015": "Swali namba kumi na moja. Mzingo wa mraba ni sentimita thelathini na sita.",
            "pg176_n0016": "Sehemu a. Eleza utakavyotafuta urefu wa kila upande.",
            "pg176_n0017": "Sehemu b. Ikiwa mraba umebadilishwa kuwa mstatili wenye upana wa sentimita tatu,",
            "pg176_n0018": "tafuta urefu wa mstatili huo.",
            "pg176_n0019": "Swali namba kumi na mbili. Mzingo wa mstatili ni mita arobaini na mbili. Upana ni mita saba. Tafuta urefu.",
            "pg176_n0021": "Swali namba kumi na tatu. Pande mbili za pembetatu zina jumla ya sentimita arobaini na nane.",
            "pg176_n0022": "Tafuta upande wa tatu ikiwa mzingo ni sentimita sitini na tisa.",
            "pg176_n0024": "Swali namba kumi na nne. Tafuta urefu wa upande mmoja wa mraba wenye mzingo wa mita tisini na mbili.",
        },
    },
    177: {
        "rate": 0.85,
        "replace": {
            "pg177_n0001": "Swali namba kumi na tano. Furaha alichora mraba wenye upande wa sentimita saba.",
            "pg177_n0002": "Mzingo wake ni sentimita ngapi?",
            "pg177_n0004": "Swali namba kumi na sita. Musa alichora mstatili wenye urefu wa sentimita nane na upana wa sentimita tano.",
            "pg177_n0005": "Mzingo wake ni sentimita ngapi?",
            "pg177_n0006": "Swali namba kumi na saba. Kitambaa kina urefu wa mita mbili na upana wa mita moja.",
            "pg177_n0008": "Mzingo wa kitambaa ni sentimita ngapi?",
            "pg177_n0009": "Swali namba kumi na nane. Zulia lina urefu wa mita saba na upana wa mita tano. Tafuta mzingo.",
            "pg177_n0011": "Swali namba kumi na tisa. Kiwanja cha mpira kina urefu wa mita mia moja na upana wa mita sabini.",
            "pg177_n0013": "Shiloli alikimbia kuzunguka kiwanja hicho. Alikimbia umbali gani?",
            "pg177_n0014": "Swali namba ishirini. Mzingo wa pembetatu ni sentimita ishirini na tatu.",
            "pg177_n0015": "Upande wa kwanza ni sentimita saba na upande wa pili ni sentimita sita.",
            "pg177_n0016": "Upande wa tatu ni sentimita ngapi?",
        },
    },
    178: {
        "rate": 0.85,
        "replace": {
            "pg178_n0001": "Jikumbushe.",
            "pg178_n0002": "Jambo la kwanza. Kipande cha mstari huoneshwa kwa nukta ya kuanzia na nukta ya kumalizia.",
            "pg178_n0004": "Jambo la pili. Mwale huoneshwa kwa nukta ya kuanzia na mshale upande mmoja.",
            "pg178_n0006": "Jambo la tatu. Mstari mnyoofu huoneshwa kwa mishale pande zote mbili.",
            "pg178_n0008": "Jambo la nne. Mzingo wa umbo bapa ni urefu wa kuzunguka umbo hilo.",
        },
    },
    186: {
        "rate": 0.85,
        "remove": {"pg186_n0006", "pg186_n0007", "pg186_n0008", "pg186_n0009", "pg186_n0010", "pg186_n0011", "pg186_n0012"},
        "replace": {
            "pg186_n0002": "Mfano.",
            "pg186_n0005": "Jedwali lina safu mbili: siku, na idadi ya mayai kwa picha. Picha moja ya yai inawakilisha mayai hamsini. Jumatatu ina picha nane. Jumanne ina picha tisa. Jumatano ina picha sita. Alhamisi ina picha saba. Ijumaa ina picha kumi. Jumamosi ina picha saba. Jumapili ina picha nne.",
            "pg186_n0014": "Swali sehemu a. Ni siku gani Maria alikusanya mayai mengi zaidi?",
            "pg186_n0015": "Swali sehemu b. Mayai mangapi yalikusanywa siku ya Jumanne?",
            "pg186_n0016": "Swali sehemu c. Mayai mangapi yalikusanywa kwa wiki?",
            "pg186_n0022": "Mayai yaliyokusanywa ni sawa na tisa kuzidisha hamsini, sawa sawa na mia nne hamsini.",
        },
    },
    187: {
        "rate": 0.85,
        "remove": {"pg187_n0014", "pg187_n0015", "pg187_n0016", "pg187_n0017", "pg187_n0018", "pg187_n0022", "pg187_n0023"},
        "replace": {
            "pg187_n0005": "Hamsini na moja kuzidisha hamsini, sawa sawa na elfu mbili mia tano hamsini.",
            "pg187_n0006": "Kwa hiyo, mayai elfu mbili mia tano hamsini yalikusanywa kwa wiki.",
            "pg187_n0007": "Zoezi la Tatu",
            "pg187_n0013": "Jedwali lina safu mbili: mwezi, na mauzo katika kilogramu kwa picha. Kipimio ni pembetatu moja inawakilisha kilogramu elfu moja. Mwezi Juni. Mauzo katika kilogramu kwa picha ni pembetatu saba. Mwezi Julai. Mauzo katika kilogramu kwa picha ni pembetatu tano. Mwezi Agosti. Mauzo katika kilogramu kwa picha ni pembetatu saba. Mwezi Septemba. Mauzo katika kilogramu kwa picha ni pembetatu tatu. Mwezi Oktoba. Mauzo katika kilogramu kwa picha ni pembetatu tisa.",
            "pg187_n0020": "Kipimio: pembetatu moja inawakilisha kilogramu elfu moja.",
            "pg187_n0021": "Swali sehemu a. Ni mwezi upi Amani aliuza nafaka chache zaidi?",
        },
    },
    188: {
        "rate": 0.85,
        "replace": {
            "pg188_n0001": "Swali sehemu b. Kilogramu ngapi ziliuzwa mwezi Agosti?",
            "pg188_n0002": "Swali sehemu c. Tafuta tofauti ya mauzo ya nafaka kwa mwezi Oktoba na Septemba.",
            "pg188_n0004": "Swali namba mbili. Tumia jedwali lifuatalo kuchora takwimu kwa picha kuonesha idadi ya wanafunzi kwa kila shule.",
            "pg188_n0006": "Jedwali lina safu mbili: shule ya msingi, na idadi ya wanafunzi.",
            "pg188_n0007": "Mstari wa kwanza. Shule ya Msingi Umoja ina wanafunzi mia nane.",
            "pg188_n0008": "Mstari wa pili. Shule ya Msingi Minazini ina wanafunzi elfu moja mia mbili.",
            "pg188_n0009": "Mstari wa tatu. Shule ya Msingi Mwenge ina wanafunzi mia tisa.",
            "pg188_n0010": "Mstari wa nne. Shule ya Msingi Kilimani ina wanafunzi elfu moja.",
            "pg188_n0011": "Mstari wa tano. Shule ya Msingi Juhudi ina wanafunzi mia sita.",
            "pg188_n0012": "Kipimio: picha moja ya mwanafunzi inawakilisha wanafunzi mia moja.",
        },
    },
    189: {
        "rate": 0.85,
        "remove": {"pg189_n0006", "pg189_n0007", "pg189_n0008", "pg189_n0009", "pg189_n0020", "pg189_n0021", "pg189_n0022", "pg189_n0023"},
        "after": {
            "pg189_n0005": [
                "Grafu ina mhimili wa wima wa idadi ya wanafunzi na mhimili wa ulalo wa madarasa. Darasa la kwanza lina wanafunzi ishirini. Darasa la pili lina wanafunzi arobaini. Darasa la tatu lina wanafunzi themanini. Darasa la nne lina wanafunzi arobaini.",
            ],
        },
        "replace": {
            "pg189_n0001": "Mfano wa Kwanza.",
            "pg189_n0010": "Kipimio: sentimita moja inawakilisha wanafunzi ishirini kwa wima.",
            "pg189_n0011": "Sentimita moja inawakilisha upana wa mhimili mmoja kwa ulalo.",
            "pg189_n0013": "Swali sehemu a. Mstari wa wima unaonesha nini?",
            "pg189_n0014": "Swali sehemu b. Mstari wa ulalo unaonesha nini?",
            "pg189_n0015": "Swali sehemu c. Darasa la Roman moja lina wanafunzi wangapi?",
            "pg189_n0016": "Swali sehemu d. Darasa lipi lina idadi kubwa ya wanafunzi?",
            "pg189_n0018": "Swali sehemu e. Madarasa yapi yana idadi sawa ya wanafunzi?",
        },
    },
    190: {
        "rate": 0.85,
        "replace": {
            "pg190_n0002": "Jibu sehemu a. Mstari wa wima unaonesha idadi ya wanafunzi.",
            "pg190_n0003": "Jibu sehemu b. Mstari wa ulalo unaonesha madarasa.",
            "pg190_n0004": "Jibu sehemu c. Darasa la Roman moja lina wanafunzi ishirini.",
            "pg190_n0005": "Jibu sehemu d. Darasa la Roman tatu lina wanafunzi wengi zaidi, ambao ni themanini.",
            "pg190_n0006": "Jibu sehemu e. Darasa la Roman mbili na Roman nne yana wanafunzi sawa,",
            "pg190_n0007": "ambao ni arobaini.",
            "pg190_n0008": "Mfano wa Pili.",
            "pg190_n0009": "Angalia mahudhurio ya wanafunzi wa darasa la nne katika Shule ya Msingi Mashujaa, kisha jibu maswali.",
            "pg190_n0011": "Jedwali lina safu za siku tano.",
            "pg190_n0013": "Jumatatu wanafunzi tisini. Jumanne mia moja ishirini. Jumatano sabini. Alhamisi sitini. Ijumaa mia moja na kumi.",
            "pg190_n0014": "Kipimio: sentimita moja inawakilisha wanafunzi ishirini kwa wima.",
            "pg190_n0015": "Sentimita moja inawakilisha upana wa mhimili mmoja kwa ulalo.",
            "pg190_n0017": "Swali sehemu a. Chora grafu kwa mihimili kuonesha taarifa hiyo.",
            "pg190_n0018": "Swali sehemu b. Mhimili wa siku gani ni mrefu zaidi?",
            "pg190_n0019": "Swali sehemu c. Mhimili wa siku gani ni mfupi zaidi?",
        },
    },
    191: {
        "rate": 0.85,
        "remove": {"pg191_n0002", "pg191_n0003", "pg191_n0004", "pg191_n0005", "pg191_n0008", "pg191_n0009", "pg191_n0010", "pg191_n0011"},
        "after": {
            "pg191_n0001": [
                "Sehemu a. Grafu kwa mihimili inaonesha mahudhurio ya wanafunzi wa darasa la nne. Mhimili wa wima unaonesha idadi ya wanafunzi. Mhimili wa ulalo unaonesha siku za Jumatatu hadi Ijumaa.",
                "Jumatatu wanafunzi tisini. Jumanne wanafunzi mia moja ishirini. Jumatano wanafunzi sabini. Alhamisi wanafunzi sitini. Ijumaa wanafunzi mia moja na kumi.",
            ],
        },
    },
    192: {
        "rate": 0.85,
        "remove": {"pg192_n0006", "pg192_n0007", "pg192_n0008", "pg192_n0009"},
        "replace": {
            "pg192_n0001": "Zoezi la Nne",
            "pg192_n0003": "Swali namba moja. Maimuna alivuna mahindi kwa miaka minne kama inavyoonekana kwenye jedwali.",
            "pg192_n0005": "Jedwali lina safu mbili: mwaka, na idadi ya magunia ya mahindi kwa picha. Mwaka elfu mbili na kumi na mbili una picha kumi za magunia. Mwaka elfu mbili na kumi na tatu una picha nane. Mwaka elfu mbili na kumi na nne una picha sita. Mwaka elfu mbili na kumi na tano una picha kumi na mbili.",
            "pg192_n0010": "Kipimio: sentimita moja inawakilisha magunia mawili kwa wima.",
            "pg192_n0011": "Sentimita moja inawakilisha upana wa mhimili mmoja kwa ulalo.",
            "pg192_n0013": "Swali sehemu a. Chora grafu kwa mihimili kuwakilisha takwimu hizo.",
            "pg192_n0014": "Swali sehemu b. Taja mwaka wenye mhimili mrefu zaidi.",
            "pg192_n0015": "Swali sehemu c. Nini tofauti kati ya mhimili wa mwaka elfu mbili na kumi na mbili na mwaka elfu mbili na kumi na tano?",
            "pg192_n0016": "Swali namba mbili. Chora grafu kwa mihimili inayoonesha matokeo ya jaribio la Hisabati,",
            "pg192_n0017": "kwa wanafunzi sita wa darasa la Roman nne, kisha jibu maswali.",
        },
    },
    193: {
        "rate": 0.85,
        "replace": {
            "pg193_n0001": "Jedwali lina safu mbili: mwanafunzi, na alama.",
            "pg193_n0002": "Bakari ana alama themanini na tano.",
            "pg193_n0003": "Amani ana alama sitini.",
            "pg193_n0004": "Neema ana alama tisini.",
            "pg193_n0005": "Shukuru ana alama arobaini.",
            "pg193_n0006": "Ashura ana alama themanini.",
            "pg193_n0007": "Bahati ana alama sitini.",
            "pg193_n0008": "Kipimio: sentimita moja inawakilisha alama kumi kwa wima.",
            "pg193_n0009": "Sentimita moja inawakilisha upana wa mhimili mmoja kwa ulalo.",
            "pg193_n0011": "Swali sehemu a. Mhimili wa nani ni mrefu zaidi?",
            "pg193_n0012": "Swali sehemu b. Tafuta tofauti ya alama kati ya mhimili mfupi zaidi na mrefu zaidi.",
            "pg193_n0014": "Swali sehemu c. Taja wanafunzi wenye mihimili inayolingana kwa urefu.",
            "pg193_n0016": "Swali namba tatu. Angalia grafu kwa mihimili inayoonesha mvua katika miezi ya Januari, Februari, Machi na Aprili,",
            "pg193_n0018": "kisha jibu maswali yanayofuata.",
        },
    },
    194: {
        "rate": 0.85,
        "remove": {
            "pg194_n0001", "pg194_n0002", "pg194_n0003", "pg194_n0004", "pg194_n0005", "pg194_n0006", "pg194_n0007", "pg194_n0008", "pg194_n0009",
            "pg194_n0010", "pg194_n0011", "pg194_n0012", "pg194_n0013", "pg194_n0014", "pg194_n0015", "pg194_n0016", "pg194_n0017", "pg194_n0018",
        },
        "replace": {
            "pg194_n0019": "Grafu kwa mihimili inaonesha kiwango cha mvua. Mhimili wa wima ni kiwango cha mvua katika milimita; mhimili wa ulalo ni miezi. Januari ina milimita sitini. Februari ina milimita mia moja. Machi ina milimita themanini. Aprili ina milimita sitini.",
            "pg194_n0020": "Kipimio: sentimita moja inawakilisha milimita ishirini za mvua kwa wima.",
            "pg194_n0021": "Sentimita moja inawakilisha upana wa mhimili mmoja kwa ulalo.",
            "pg194_n0023": "Swali sehemu a. Mwezi gani mvua ilinyesha nyingi zaidi?",
            "pg194_n0024": "Swali sehemu b. Miezi ipi ilikuwa na kiwango sawa cha mvua?",
            "pg194_n0025": "Swali sehemu c. Mwezi Machi mvua ilinyesha kwa kiwango gani?",
        },
    },
    172: {"rate": 0.85, "replace": {
        "pg172_n0001": "Zoezi la Saba.",
        "pg172_n0002": "Tafuta mzingo wa maumbo bapa yafuatayo. Usihesabu jibu mpaka usikie vipimo vya pande zote.",
    }, "after": {"pg172_n0002": [
        "Umbo namba moja ni mstatili. Urefu wake ni mita kumi na tisa. Upana wake ni mita saba.",
        "Umbo namba mbili ni mraba. Kila upande una urefu wa mita nane.",
        "Umbo namba tatu ni mraba. Kila upande una urefu wa mita kumi na mbili.",
        "Umbo namba nne ni pembetatu. Pande zake zina urefu wa sentimita tisa, sentimita saba na sentimita kumi na nane.",
        "Umbo namba tano ni pembetatu. Pande zake zina urefu wa sentimita tisa, sentimita tisa na sentimita kumi na moja.",
        "Umbo namba sita ni mraba. Kila upande una urefu wa mita kumi.",
        "Umbo namba saba ni mstatili. Urefu wake ni sentimita thelathini na mbili. Upana wake ni sentimita kumi na tatu.",
        "Umbo namba nane ni pembetatu. Pande zake zina urefu wa sentimita sita, sentimita nane na sentimita kumi na mbili.",
    ]}},
    179: {"rate": 0.85, "replace": {
        "pg179_n0001": "Sura ya Kumi na Tatu.",
        "pg179_n0013": "Zoezi la Kwanza: Marudio.",
    }, "after": {"pg179_n0014": [
        "Jedwali lina aina tano za matunda. Majina ya matunda ni mananasi, ndizi, matufaha, machungwa na embe.",
        "Mananasi ni matano. Ndizi ni nne. Matufaha ni manne. Machungwa ni manne. Embe ni moja. Jumla ya matunda yote ni kumi na nane.",
    ]}},
    180: {
        "rate": 0.85,
        "replace": {
            "pg180_n0001": "Maswali.",
            "pg180_n0002": "Swali namba moja. Chora au tenga makundi ya matunda yanayofanana.",
            "pg180_n0003": "Swali namba mbili. Andika idadi ya matunda kwa kila kundi.",
            "pg180_n0004": "Swali namba tatu. Matunda yapi ni mengi zaidi?",
            "pg180_n0005": "Swali namba nne. Matunda yapi ni machache zaidi?",
            "pg180_n0006": "Swali namba tano. Matunda yapi yana idadi sawa?",
            "pg180_n0012": "Kwa mfano, mama alinunua vyombo vya chakula: bilauri tatu, sufuria mbili, vikombe vinne na vijiko kumi.",
        },
        "after": {"pg180_n0014": [
            "Jedwali lina safu tatu. Safu ya kwanza ina jina la chombo. Safu ya pili ina idadi ya vyombo kwa picha. Safu ya tatu ina idadi ya vyombo kwa tarakimu.",
            "Mstari wa kwanza una bilauri. Kuna picha tatu za bilauri. Idadi kwa tarakimu ni tatu. Mstari wa pili una sufuria. Kuna picha mbili za sufuria. Idadi kwa tarakimu ni mbili.",
        ]},
    },
    181: {
        "rate": 0.85,
        "remove": {"pg181_n0013", "pg181_n0014"},
        "after": {
            "pg181_n0005": [
                "Huu ni mwendelezo wa jedwali la vyombo.",
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
    ]}, "rate": 0.85, "replace": {
        "pg182_n0014": "Hatua.",
        "pg182_n0015": "Hatua ya kwanza. Baini aina ya picha katika taarifa kwa kila kundi.",
        "pg182_n0016": "Hatua ya pili. Hesabu idadi ya picha kulingana na makundi.",
        "pg182_n0017": "Hatua ya tatu. Soma maelezo yanayofafanua picha hizo.",
        "pg182_n0018": "Hatua ya nne. Soma, tafsiri na uandike takwimu kwa usahihi kutokana na picha.",
    }},
    183: {
        "rate": 0.85,
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
    }, "rate": 0.85},
    185: {"replace": {
        "pg185_n0001": "Mwendelezo wa jedwali. Viazi vina picha thelathini za magunia. Picha hizo zinawakilisha magunia elfu thelathini.",
        "pg185_n0002": "Mtama una picha nane za magunia. Picha hizo zinawakilisha magunia elfu nane.",
        "pg185_n0003": "Zoezi la Pili.",
        "pg185_n0004": "Jaza nafasi zilizo wazi katika jedwali. Namba moja imefanyika kama mfano.",
        "pg185_n0006": "Jedwali lina safu nne: namba, idadi, idadi kwa picha, na kipimio.",
        "pg185_n0008": "Mstari wa kwanza, mfano. Miti elfu kumi na tano. Idadi kwa picha ni miti kumi na tano. Picha moja ya mti inawakilisha miti elfu moja.",
        "pg185_n0010": "Mstari wa pili. Mayai elfu kumi na moja. Sehemu ya idadi kwa picha ni wazi. Picha moja ya yai inawakilisha mayai elfu moja.",
        "pg185_n0012": "Mstari wa tatu. Boksi mia mbili. Sehemu ya idadi kwa picha ni wazi. Picha moja ya boksi inawakilisha boksi mia moja.",
        "pg185_n0014": "Mstari wa nne. Magunia ya karanga elfu arobaini. Sehemu ya idadi kwa picha ni wazi.",
        "pg185_n0015": "Picha moja ya gunia inawakilisha magunia elfu kumi.",
        "pg185_n0017": "Mstari wa tano. Machungwa elfu themanini. Sehemu ya idadi kwa picha ni wazi.",
        "pg185_n0018": "Picha moja ya chungwa inawakilisha machungwa elfu kumi.",
        "pg185_n0020": "Mstari wa sita. Chupa hamsini za maji. Sehemu ya idadi kwa picha ni wazi.",
        "pg185_n0021": "Picha moja ya chupa inawakilisha chupa kumi.",
    }, "rate": 0.85},
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
    from fix_full_book_audio import number_to_swahili

    normalized = [norm(text) for _, text in words]
    cursor = 0
    last = words[0][0] if words else 0
    for cue in cues:
        needle = norm(cue["text"])
        found = next((i for i in range(cursor, len(words)) if normalized[i] == needle), -1)
        if found >= 0:
            last, cursor = words[found][0], found + 1
        cue["sourceIndex"] = last

    # Rewritten educational narration spells out printed digits and operators.
    # Point every spoken part back to the real word or symbol on the page so
    # the yellow reading shadow remains on the book itself.
    cue_norms = [norm(cue["text"]) for cue in cues]
    numeric_targets = {}
    symbol_targets = {"kuzidisha": [], "kugawanya": [], "jumlisha": [], "kutoa": [], "sawa": []}
    for source_index, visible in words:
        stripped = visible.strip()
        match = re.fullmatch(r"(\d+)[.,:]?", stripped)
        if match:
            numeric_targets.setdefault(int(match.group(1)), []).append(source_index)
        if "×" in stripped:
            symbol_targets["kuzidisha"].append(source_index)
        if "÷" in stripped:
            symbol_targets["kugawanya"].append(source_index)
        if "+" in stripped:
            symbol_targets["jumlisha"].append(source_index)
        if "−" in stripped or re.fullmatch(r"-", stripped):
            symbol_targets["kutoa"].append(source_index)
        if "=" in stripped:
            symbol_targets["sawa"].append(source_index)

    used_numeric = {value: 0 for value in numeric_targets}
    numeric_candidates = []
    for value in numeric_targets:
        base = [norm(token) for token in number_to_swahili(value).split()]
        na_positions = [i for i, token in enumerate(base) if token == "na"]
        variants = {tuple(base)}
        for mask in range(1 << len(na_positions)):
            removed = {na_positions[i] for i in range(len(na_positions)) if mask & (1 << i)}
            variants.add(tuple(token for i, token in enumerate(base) if i not in removed))
        for variant in variants:
            if variant:
                numeric_candidates.append((len(variant), value, variant))
    numeric_candidates.sort(reverse=True)

    i = 0
    while i < len(cues):
        matched = None
        for length, value, variant in numeric_candidates:
            if tuple(cue_norms[i:i + length]) == variant and used_numeric[value] < len(numeric_targets[value]):
                matched = (length, value)
                break
        if not matched:
            i += 1
            continue
        length, value = matched
        source_index = numeric_targets[value][used_numeric[value]]
        used_numeric[value] += 1
        prefix_start = i
        if i >= 2 and cue_norms[i - 2:i] == ["swali", "namba"]:
            prefix_start = i - 2
        for cue_index in range(prefix_start, i + length):
            cues[cue_index].pop("targetImage", None)
            cues[cue_index]["sourceIndex"] = source_index
        i += length

    for spoken, targets in symbol_targets.items():
        target_pos = 0
        for cue_index, cue_norm in enumerate(cue_norms):
            if cue_norm != spoken or target_pos >= len(targets):
                continue
            cues[cue_index].pop("targetImage", None)
            cues[cue_index]["sourceIndex"] = targets[target_pos]
            if spoken == "sawa":
                for extra in (1, 2):
                    if cue_index + extra < len(cues) and cue_norms[cue_index + extra] in {"sawa", "na"}:
                        cues[cue_index + extra].pop("targetImage", None)
                        cues[cue_index + extra]["sourceIndex"] = targets[target_pos]
            target_pos += 1


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


def pronounce_roman_letters(value):
    pronunciations = {
        "I": "aii",
        "V": "vii",
        "X": "exi",
        "L": "eli",
        "C": "sii",
        "D": "dii",
        "M": "emu",
    }
    return re.sub(
        r"(?<![A-Za-z])([IVXLCDM]+)(?![A-Za-z])",
        lambda match: " ".join(pronunciations[letter] for letter in match.group(1)),
        value,
    )


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
        if page in {49, 52, 55, 56}:
            segment_text = re.sub(
                r"(?<!\d)(\d+)(?!\d)",
                lambda match: number_to_swahili(int(match.group(1))),
                segment_text,
            )
        if page == 20:
            segment_text = re.sub(r"(?<!\d)10001(?!\d)", "elfu kumi na moja", segment_text)
        segment_text = pronounce_roman_letters(segment_text)
        segments.append((segment_text, "source"))
        for extra in after.get(node_id, []):
            kind = "table" if page == 7 and node_id == "pg007_n0012" else "image"
            segments.append((pronounce_roman_letters(extra), kind))
    text = " ".join(value for value, _ in segments)
    cues = []
    audio_name = f"page-{page:03d}-matrix-v32.mp3"
    output = ROOT / "content" / "rehema"
    audio_path = output / audio_name
    temp_path = output / f".{audio_name}.tmp"
    with temp_path.open("wb") as audio:
        requested_rate = float(cfg.get("rate", 0.8 if 8 <= page <= 15 or page == 17 else 0.9))
        page_rate = f"{round((requested_rate - 1) * 100):+d}%"
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
                cue.pop("targetImage", None)
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
    default_rate = 0.8 if 8 <= page <= 15 or page == 17 else 0.9
    entry = {"audio": audio_name, "voice": VOICE, "rate": cfg.get("rate", default_rate), "pitch": "neutral", "version": 47, "words": cues}
    (output / f"page-{page:03d}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
    timecodes[str(page)] = entry
    path.write_text(patch_transcript(raw, replacements, after, cfg.get("remove", set())), encoding="utf-8")
    print(f"page={page} words={len(cues)} audio={audio_name}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcripts-only", action="store_true")
    parser.add_argument("--page", type=int)
    parser.add_argument("--pages", help="Comma-separated page numbers")
    args = parser.parse_args()
    requested_pages = [int(value) for value in args.pages.split(",")] if args.pages else None
    timecodes_path = ROOT / "content" / "rehema" / "timecodes.json"
    timecodes = json.loads(timecodes_path.read_text(encoding="utf-8"))
    if args.transcripts_only:
        selected = CONFIG.items()
        if args.page is not None:
            selected = [(args.page, CONFIG[args.page])]
        elif requested_pages is not None:
            selected = [(page, CONFIG[page]) for page in requested_pages]
        for page, cfg in selected:
            path, raw, _, _ = source(page)
            updated = patch_transcript(raw, cfg.get("replace", {}), cfg.get("after", {}), cfg.get("remove", set()))
            path.write_text(updated, encoding="utf-8")
            print(f"page={page} transcript=updated")
        return
    selected_pages = CONFIG
    if args.page is not None:
        selected_pages = [args.page]
    elif requested_pages is not None:
        selected_pages = requested_pages
    for page in selected_pages:
        await generate(page, timecodes)
    timecodes_path.write_text(json.dumps(timecodes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())

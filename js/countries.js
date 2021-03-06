// countries
var ENABLED_COUNTRIES = ['US', 'DE', 'CA'];

var COUNTRIES = {
	"AF":{
		"name":"Afghanistan",
		"subdivisions":{},
	},
	"AX":{
		"name":"Åland Islands",
		"subdivisions":{},
	},
	"AL":{
		"name":"Albania",
		"subdivisions":{},
	},
	"DZ":{
		"name":"Algeria",
		"subdivisions":{},
	},
	"AS":{
		"name":"American Samoa",
		"subdivisions":{},
	},
	"AD":{
		"name":"Andorra",
		"subdivisions":{},
	},
	"AO":{
		"name":"Angola",
		"subdivisions":{},
	},
	"AI":{
		"name":"Anguilla",
		"subdivisions":{},
	},
	"AQ":{
		"name":"Antarctica",
		"subdivisions":{},
	},
	"AG":{
		"name":"Antigua and Barbuda",
		"subdivisions":{},
	},
	"AR":{
		"name":"Argentina",
		"subdivisions":{},
	},
	"AM":{
		"name":"Armenia",
		"subdivisions":{},
	},
	"AW":{
		"name":"Aruba",
		"subdivisions":{},
	},
	"AU":{
		"name":"Australia",
		"subdivisions":{},
	},
	"AT":{
		"name":"Austria",
		"subdivisions":{},
	},
	"AZ":{
		"name":"Azerbaijan",
		"subdivisions":{},
	},
	"BS":{
		"name":"Bahamas",
		"subdivisions":{},
	},
	"BH":{
		"name":"Bahrain",
		"subdivisions":{},
	},
	"BD":{
		"name":"Bangladesh",
		"subdivisions":{},
	},
	"BB":{
		"name":"Barbados",
		"subdivisions":{},
	},
	"BY":{
		"name":"Belarus",
		"subdivisions":{},
	},
	"BE":{
		"name":"Belgium",
		"subdivisions":{},
	},
	"BZ":{
		"name":"Belize",
		"subdivisions":{},
	},
	"BJ":{
		"name":"Benin",
		"subdivisions":{},
	},
	"BM":{
		"name":"Bermuda",
		"subdivisions":{},
	},
	"BT":{
		"name":"Bhutan",
		"subdivisions":{},
	},
	"BO":{
		"name":"Bolivia, Plurinational State of",
		"subdivisions":{},
	},
	"BQ":{
		"name":"Bonaire, Sint Eustatius and Saba",
		"subdivisions":{},
	},
	"BA":{
		"name":"Bosnia and Herzegovina",
		"subdivisions":{},
	},
	"BW":{
		"name":"Botswana",
		"subdivisions":{},
	},
	"BV":{
		"name":"Bouvet Island",
		"subdivisions":{},
	},
	"BR":{
		"name":"Brazil",
		"subdivisions":{},
	},
	"IO":{
		"name":"British Indian Ocean Territory",
		"subdivisions":{},
	},
	"BN":{
		"name":"Brunei Darussalam",
		"subdivisions":{},
	},
	"BG":{
		"name":"Bulgaria",
		"subdivisions":{},
	},
	"BF":{
		"name":"Burkina Faso",
		"subdivisions":{},
	},
	"BI":{
		"name":"Burundi",
		"subdivisions":{},
	},
	"KH":{
		"name":"Cambodia",
		"subdivisions":{},
	},
	"CM":{
		"name":"Cameroon",
		"subdivisions":{},
	},
	"CA":{
		"name":"Canada",
		"subdivisions":{
			"CA-AB":"Alberta",
			"CA-BC":"British Columbia",
			"CA-MB":"Manitoba",
			"CA-NB":"New Brunswick",
			"CA-NL":"Newfoundland and Labrador",
			"CA-NS":"Nova Scotia",
			"CA-ON":"Ontario",
			"CA-PE":"Prince Edward Island",
			"CA-QC":"Quebec",
			"CA-SK":"Saskatchewan",
			"CA-NT":"Northwest Territories",
			"CA-NU":"Nunavut",
			"CA-YT":"Yukon Territory"
		},
	},
	"CV":{
		"name":"Cape Verde",
		"subdivisions":{},
	},
	"KY":{
		"name":"Cayman Islands",
		"subdivisions":{},
	},
	"CF":{
		"name":"Central African Republic",
		"subdivisions":{},
	},
	"TD":{
		"name":"Chad",
		"subdivisions":{},
	},
	"CL":{
		"name":"Chile",
		"subdivisions":{},
	},
	"CN":{
		"name":"China",
		"subdivisions":{},
	},
	"CX":{
		"name":"Christmas Island",
		"subdivisions":{},
	},
	"CC":{
		"name":"Cocos (Keeling) Islands",
		"subdivisions":{},
	},
	"CO":{
		"name":"Colombia",
		"subdivisions":{},
	},
	"KM":{
		"name":"Comoros",
		"subdivisions":{},
	},
	"CG":{
		"name":"Congo",
		"subdivisions":{},
	},
	"CD":{
		"name":"Congo, the Democratic Republic of the",
		"subdivisions":{},
	},
	"CK":{
		"name":"Cook Islands",
		"subdivisions":{},
	},
	"CR":{
		"name":"Costa Rica",
		"subdivisions":{},
	},
	"CI":{
		"name":"Côte d'Ivoire",
		"subdivisions":{},
	},
	"HR":{
		"name":"Croatia",
		"subdivisions":{},
	},
	"CU":{
		"name":"Cuba",
		"subdivisions":{},
	},
	"CW":{
		"name":"Curaçao",
		"subdivisions":{},
	},
	"CY":{
		"name":"Cyprus",
		"subdivisions":{},
	},
	"CZ":{
		"name":"Czech Republic",
		"subdivisions":{},
	},
	"DK":{
		"name":"Denmark",
		"subdivisions":{},
	},
	"DJ":{
		"name":"Djibouti",
		"subdivisions":{},
	},
	"DM":{
		"name":"Dominica",
		"subdivisions":{},
	},
	"DO":{
		"name":"Dominican Republic",
		"subdivisions":{},
	},
	"EC":{
		"name":"Ecuador",
		"subdivisions":{},
	},
	"EG":{
		"name":"Egypt",
		"subdivisions":{},
	},
	"SV":{
		"name":"El Salvador",
		"subdivisions":{},
	},
	"GQ":{
		"name":"Equatorial Guinea",
		"subdivisions":{},
	},
	"ER":{
		"name":"Eritrea",
		"subdivisions":{},
	},
	"EE":{
		"name":"Estonia",
		"subdivisions":{},
	},
	"ET":{
		"name":"Ethiopia",
		"subdivisions":{},
	},
	"FK":{
		"name":"Falkland Islands (Malvinas)",
		"subdivisions":{},
	},
	"FO":{
		"name":"Faroe Islands",
		"subdivisions":{},
	},
	"FJ":{
		"name":"Fiji",
		"subdivisions":{},
	},
	"FI":{
		"name":"Finland",
		"subdivisions":{},
	},
	"FR":{
		"name":"France",
		"subdivisions":{},
	},
	"GF":{
		"name":"French Guiana",
		"subdivisions":{},
	},
	"PF":{
		"name":"French Polynesia",
		"subdivisions":{},
	},
	"TF":{
		"name":"French Southern Territories",
		"subdivisions":{},
	},
	"GA":{
		"name":"Gabon",
		"subdivisions":{},
	},
	"GM":{
		"name":"Gambia",
		"subdivisions":{},
	},
	"GE":{
		"name":"Georgia",
		"subdivisions":{},
	},
	"DE":{
		"name":"Germany",
		"subdivisions":{
			"DE-BW":"Baden-Württemberg",
			"DE-BY":"Bayern",
			"DE-BE":"Berlin",
			"DE-BB":"Brandenburg",
			"DE-HB":"Bremen",
			"DE-HH":"Hamburg",
			"DE-HE":"Hessen",
			"DE-MV":"Mecklenburg-Vorpommern",
			"DE-NI":"Niedersachsen",
			"DE-NW":"Nordrhein-Westfalen",
			"DE-RP":"Rheinland-Pfalz",
			"DE-SL":"Saarland",
			"DE-SN":"Sachsen",
			"DE-ST":"Sachsen-Anhalt",
			"DE-SH":"Schleswig-Holstein",
			"DE-TH":"Thüringen"
		}
	},
	"GH":{
		"name":"Ghana",
		"subdivisions":{},
	},
	"GI":{
		"name":"Gibraltar",
		"subdivisions":{},
	},
	"GR":{
		"name":"Greece",
		"subdivisions":{},
	},
	"GL":{
		"name":"Greenland",
		"subdivisions":{},
	},
	"GD":{
		"name":"Grenada",
		"subdivisions":{},
	},
	"GP":{
		"name":"Guadeloupe",
		"subdivisions":{},
	},
	"GU":{
		"name":"Guam",
		"subdivisions":{},
	},
	"GT":{
		"name":"Guatemala",
		"subdivisions":{},
	},
	"GG":{
		"name":"Guernsey",
		"subdivisions":{},
	},
	"GN":{
		"name":"Guinea",
		"subdivisions":{},
	},
	"GW":{
		"name":"Guinea-Bissau",
		"subdivisions":{},
	},
	"GY":{
		"name":"Guyana",
		"subdivisions":{},
	},
	"HT":{
		"name":"Haiti",
		"subdivisions":{},
	},
	"HM":{
		"name":"Heard Island and McDonald Islands",
		"subdivisions":{},
	},
	"VA":{
		"name":"Holy See (Vatican City State)",
		"subdivisions":{},
	},
	"HN":{
		"name":"Honduras",
		"subdivisions":{},
	},
	"HK":{
		"name":"Hong Kong",
		"subdivisions":{},
	},
	"HU":{
		"name":"Hungary",
		"subdivisions":{},
	},
	"IS":{
		"name":"Iceland",
		"subdivisions":{},
	},
	"IN":{
		"name":"India",
		"subdivisions":{},
	},
	"ID":{
		"name":"Indonesia",
		"subdivisions":{},
	},
	"IR":{
		"name":"Iran, Islamic Republic of",
		"subdivisions":{},
	},
	"IQ":{
		"name":"Iraq",
		"subdivisions":{},
	},
	"IE":{
		"name":"Ireland",
		"subdivisions":{},
	},
	"IM":{
		"name":"Isle of Man",
		"subdivisions":{},
	},
	"IL":{
		"name":"Israel",
		"subdivisions":{},
	},
	"IT":{
		"name":"Italy",
		"subdivisions":{},
	},
	"JM":{
		"name":"Jamaica",
		"subdivisions":{},
	},
	"JP":{
		"name":"Japan",
		"subdivisions":{},
	},
	"JE":{
		"name":"Jersey",
		"subdivisions":{},
	},
	"JO":{
		"name":"Jordan",
		"subdivisions":{},
	},
	"KZ":{
		"name":"Kazakhstan",
		"subdivisions":{},
	},
	"KE":{
		"name":"Kenya",
		"subdivisions":{},
	},
	"KI":{
		"name":"Kiribati",
		"subdivisions":{},
	},
	"KP":{
		"name":"Korea, Democratic People's Republic of",
		"subdivisions":{},
	},
	"KR":{
		"name":"Korea, Republic of",
		"subdivisions":{},
	},
	"KW":{
		"name":"Kuwait",
		"subdivisions":{},
	},
	"KG":{
		"name":"Kyrgyzstan",
		"subdivisions":{},
	},
	"LA":{
		"name":"Lao People's Democratic Republic",
		"subdivisions":{},
	},
	"LV":{
		"name":"Latvia",
		"subdivisions":{},
	},
	"LB":{
		"name":"Lebanon",
		"subdivisions":{},
	},
	"LS":{
		"name":"Lesotho",
		"subdivisions":{},
	},
	"LR":{
		"name":"Liberia",
		"subdivisions":{},
	},
	"LY":{
		"name":"Libya",
		"subdivisions":{},
	},
	"LI":{
		"name":"Liechtenstein",
		"subdivisions":{},
	},
	"LT":{
		"name":"Lithuania",
		"subdivisions":{},
	},
	"LU":{
		"name":"Luxembourg",
		"subdivisions":{},
	},
	"MO":{
		"name":"Macao",
		"subdivisions":{},
	},
	"MK":{
		"name":"Macedonia, The Former Yugoslav Republic of",
		"subdivisions":{},
	},
	"MG":{
		"name":"Madagascar",
		"subdivisions":{},
	},
	"MW":{
		"name":"Malawi",
		"subdivisions":{},
	},
	"MY":{
		"name":"Malaysia",
		"subdivisions":{},
	},
	"MV":{
		"name":"Maldives",
		"subdivisions":{},
	},
	"ML":{
		"name":"Mali",
		"subdivisions":{},
	},
	"MT":{
		"name":"Malta",
		"subdivisions":{},
	},
	"MH":{
		"name":"Marshall Islands",
		"subdivisions":{},
	},
	"MQ":{
		"name":"Martinique",
		"subdivisions":{},
	},
	"MR":{
		"name":"Mauritania",
		"subdivisions":{},
	},
	"MU":{
		"name":"Mauritius",
		"subdivisions":{},
	},
	"YT":{
		"name":"Mayotte",
		"subdivisions":{},
	},
	"MX":{
		"name":"Mexico",
		"subdivisions":{},
	},
	"FM":{
		"name":"Micronesia, Federated States of",
		"subdivisions":{},
	},
	"MD":{
		"name":"Moldova, Republic of",
		"subdivisions":{},
	},
	"MC":{
		"name":"Monaco",
		"subdivisions":{},
	},
	"MN":{
		"name":"Mongolia",
		"subdivisions":{},
	},
	"ME":{
		"name":"Montenegro",
		"subdivisions":{},
	},
	"MS":{
		"name":"Montserrat",
		"subdivisions":{},
	},
	"MA":{
		"name":"Morocco",
		"subdivisions":{},
	},
	"MZ":{
		"name":"Mozambique",
		"subdivisions":{},
	},
	"MM":{
		"name":"Myanmar",
		"subdivisions":{},
	},
	"NA":{
		"name":"Namibia",
		"subdivisions":{},
	},
	"NR":{
		"name":"Nauru",
		"subdivisions":{},
	},
	"NP":{
		"name":"Nepal",
		"subdivisions":{},
	},
	"NL":{
		"name":"Netherlands",
		"subdivisions":{},
	},
	"NC":{
		"name":"New Caledonia",
		"subdivisions":{},
	},
	"NZ":{
		"name":"New Zealand",
		"subdivisions":{},
	},
	"NI":{
		"name":"Nicaragua",
		"subdivisions":{},
	},
	"NE":{
		"name":"Niger",
		"subdivisions":{},
	},
	"NG":{
		"name":"Nigeria",
		"subdivisions":{},
	},
	"NU":{
		"name":"Niue",
		"subdivisions":{},
	},
	"NF":{
		"name":"Norfolk Island",
		"subdivisions":{},
	},
	"MP":{
		"name":"Northern Mariana Islands",
		"subdivisions":{},
	},
	"NO":{
		"name":"Norway",
		"subdivisions":{},
	},
	"OM":{
		"name":"Oman",
		"subdivisions":{},
	},
	"PK":{
		"name":"Pakistan",
		"subdivisions":{},
	},
	"PW":{
		"name":"Palau",
		"subdivisions":{},
	},
	"PS":{
		"name":"Palestine, State of",
		"subdivisions":{},
	},
	"PA":{
		"name":"Panama",
		"subdivisions":{},
	},
	"PG":{
		"name":"Papua New Guinea",
		"subdivisions":{},
	},
	"PY":{
		"name":"Paraguay",
		"subdivisions":{},
	},
	"PE":{
		"name":"Peru",
		"subdivisions":{},
	},
	"PH":{
		"name":"Philippines",
		"subdivisions":{},
	},
	"PN":{
		"name":"Pitcairn",
		"subdivisions":{},
	},
	"PL":{
		"name":"Poland",
		"subdivisions":{},
	},
	"PT":{
		"name":"Portugal",
		"subdivisions":{},
	},
	"PR":{
		"name":"Puerto Rico",
		"subdivisions":{},
	},
	"QA":{
		"name":"Qatar",
		"subdivisions":{},
	},
	"RE":{
		"name":"Réunion",
		"subdivisions":{},
	},
	"RO":{
		"name":"Romania",
		"subdivisions":{},
	},
	"RU":{
		"name":"Russian Federation",
		"subdivisions":{},
	},
	"RW":{
		"name":"Rwanda",
		"subdivisions":{},
	},
	"BL":{
		"name":"Saint Barthélemy",
		"subdivisions":{},
	},
	"SH":{
		"name":"Saint Helena, Ascension and Tristan da Cunha",
		"subdivisions":{},
	},
	"KN":{
		"name":"Saint Kitts and Nevis",
		"subdivisions":{},
	},
	"LC":{
		"name":"Saint Lucia",
		"subdivisions":{},
	},
	"MF":{
		"name":"Saint Martin (French part)",
		"subdivisions":{},
	},
	"PM":{
		"name":"Saint Pierre and Miquelon",
		"subdivisions":{},
	},
	"VC":{
		"name":"Saint Vincent and the Grenadines",
		"subdivisions":{},
	},
	"WS":{
		"name":"Samoa",
		"subdivisions":{},
	},
	"SM":{
		"name":"San Marino",
		"subdivisions":{},
	},
	"ST":{
		"name":"Sao Tome and Principe",
		"subdivisions":{},
	},
	"SA":{
		"name":"Saudi Arabia",
		"subdivisions":{},
	},
	"SN":{
		"name":"Senegal",
		"subdivisions":{},
	},
	"RS":{
		"name":"Serbia",
		"subdivisions":{},
	},
	"SC":{
		"name":"Seychelles",
		"subdivisions":{},
	},
	"SL":{
		"name":"Sierra Leone",
		"subdivisions":{},
	},
	"SG":{
		"name":"Singapore",
		"subdivisions":{},
	},
	"SX":{
		"name":"Sint Maarten (Dutch part)",
		"subdivisions":{},
	},
	"SK":{
		"name":"Slovakia",
		"subdivisions":{},
	},
	"SI":{
		"name":"Slovenia",
		"subdivisions":{},
	},
	"SB":{
		"name":"Solomon Islands",
		"subdivisions":{},
	},
	"SO":{
		"name":"Somalia",
		"subdivisions":{},
	},
	"ZA":{
		"name":"South Africa",
		"subdivisions":{},
	},
	"GS":{
		"name":"South Georgia and the South Sandwich Islands",
		"subdivisions":{},
	},
	"SS":{
		"name":"South Sudan",
		"subdivisions":{},
	},
	"ES":{
		"name":"Spain",
		"subdivisions":{},
	},
	"LK":{
		"name":"Sri Lanka",
		"subdivisions":{},
	},
	"SD":{
		"name":"Sudan",
		"subdivisions":{},
	},
	"SR":{
		"name":"Suriname",
		"subdivisions":{},
	},
	"SJ":{
		"name":"Svalbard and Jan Mayen",
		"subdivisions":{},
	},
	"SZ":{
		"name":"Swaziland",
		"subdivisions":{},
	},
	"SE":{
		"name":"Sweden",
		"subdivisions":{},
	},
	"CH":{
		"name":"Switzerland",
		"subdivisions":{},
	},
	"SY":{
		"name":"Syrian Arab Republic",
		"subdivisions":{},
	},
	"TW":{
		"name":"Taiwan, Province of China",
		"subdivisions":{},
	},
	"TJ":{
		"name":"Tajikistan",
		"subdivisions":{},
	},
	"TZ":{
		"name":"Tanzania, United Republic of",
		"subdivisions":{},
	},
	"TH":{
		"name":"Thailand",
		"subdivisions":{},
	},
	"TL":{
		"name":"Timor-Leste",
		"subdivisions":{},
	},
	"TG":{
		"name":"Togo",
		"subdivisions":{},
	},
	"TK":{
		"name":"Tokelau",
		"subdivisions":{},
	},
	"TO":{
		"name":"Tonga",
		"subdivisions":{},
	},
	"TT":{
		"name":"Trinidad and Tobago",
		"subdivisions":{},
	},
	"TN":{
		"name":"Tunisia",
		"subdivisions":{},
	},
	"TR":{
		"name":"Turkey",
		"subdivisions":{},
	},
	"TM":{
		"name":"Turkmenistan",
		"subdivisions":{},
	},
	"TC":{
		"name":"Turks and Caicos Islands",
		"subdivisions":{},
	},
	"TV":{
		"name":"Tuvalu",
		"subdivisions":{},
	},
	"UG":{
		"name":"Uganda",
		"subdivisions":{},
	},
	"UA":{
		"name":"Ukraine",
		"subdivisions":{},
	},
	"AE":{
		"name":"United Arab Emirates",
		"subdivisions":{},
	},
	"GB":{
		"name":"United Kingdom",
		"subdivisions":{},
	},
	"US":{
		"name":"United States",
		"subdivisions": {
	   		"US-AL":"Alabama",
			"US-AK":"Alaska",
			"US-AS":"American Samoa",
			"US-AZ":"Arizona",
			"US-AR":"Arkansas",
			"US-CA":"California",
			"US-CO":"Colorado",
			"US-CT":"Connecticut",
			"US-DE":"Delaware",
			"US-DC":"District of Columbia",
			"US-FL":"Florida",
			"US-GA":"Georgia",
			"US-GU":"Guam",
			"US-HI":"Hawaii",
			"US-ID":"Idaho",
			"US-IL":"Illinois",
			"US-IN":"Indiana",
			"US-IA":"Iowa",
			"US-KS":"Kansas",
			"US-KY":"Kentucky",
			"US-LA":"Louisiana",
			"US-ME":"Maine",
			"US-MD":"Maryland",
			"US-MA":"Massachusetts",
			"US-MI":"Michigan",
			"US-MN":"Minnesota",
			"US-MS":"Mississippi",
			"US-MO":"Missouri",
			"US-MT":"Montana",
			"US-NE":"Nebraska",
			"US-NV":"Nevada",
			"US-NH":"New Hampshire",
			"US-NJ":"New Jersey",
			"US-NM":"New Mexico",
			"US-NY":"New York",
			"US-NC":"North Carolina",
			"US-ND":"North Dakota",
			"US-MP":"Northern Mariana Islands",
			"US-OH":"Ohio",
			"US-OK":"Oklahoma",
			"US-OR":"Oregon",
			"US-PA":"Pennsylvania",
			"US-PR":"Puerto Rico",
			"US-RI":"Rhode Island",
			"US-SC":"South Carolina",
			"US-SD":"South Dakota",
			"US-TN":"Tennessee",
			"US-TX":"Texas",
			"US-UM":"United States Minor Outlying Islands",
			"US-UT":"Utah",
			"US-VT":"Vermont",
			"US-VI":"Virgin Islands, U.S.",
			"US-VA":"Virginia",
			"US-WA":"Washington",
			"US-WV":"West Virginia",
			"US-WI":"Wisconsin",
			"US-WY":"Wyoming"
		}
	},
	"UM":{
		"name":"United States Minor Outlying Islands",
		"subdivisions":{},
	},
	"UY":{
		"name":"Uruguay",
		"subdivisions":{},
	},
	"UZ":{
		"name":"Uzbekistan",
		"subdivisions":{},
	},
	"VU":{
		"name":"Vanuatu",
		"subdivisions":{},
	},
	"VE":{
		"name":"Venezuela, Bolivarian Republic of",
		"subdivisions":{},
	},
	"VN":{
		"name":"Viet Nam",
		"subdivisions":{},
	},
	"VG":{
		"name":"Virgin Islands, British",
		"subdivisions":{},
	},
	"VI":{
		"name":"Virgin Islands, U.S.",
		"subdivisions":{},
	},
	"WF":{
		"name":"Wallis and Futuna",
		"subdivisions":{},
	},
	"EH":{
		"name":"Western Sahara",
		"subdivisions":{},
	},
	"YE":{
		"name":"Yemen",
		"subdivisions":{},
	},
	"ZM":{
		"name":"Zambia",
		"subdivisions":{},
	},
	"ZW":{
		"name":"Zimbabwe",
		"subdivisions":{},
	}
}
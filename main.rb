#!/usr/bin/env ruby

require 'rubygems'
require 'mail'
require 'csv'    


TENTA_LINK = 'https://student.portal.chalmers.se/sv/chalmersstudier/regelsamling/Sidor/F%C3%B6reskrifter-examination.aspx'

PARTS = {
	:purpose => "kursens syfte och lärandemål",
	:examiner => "examinator, föreläsare, övnings-/laborationshandledare, administrativ personal samt deras kontaktuppgifter",
	:litterature => "kurslitteratur",
	:plan => "plan för föreläsningar, övningar och laborationer",
	:changes => "en sammanfattning av gjorda förändringar sedan förra tillfället",
	:examination_form => "form för examinationen",
	:grading_scale => "betygsgränser och eventuella övriga krav för att bli godkänd på kursen (obligatoriska moment)",
	:mandatory_parts => "hur obligatoriska moment bidrar till slutbetyget",
	:volentary_parts => "hur frivilliga moment bidrar till bedömningen av de studerandes kunskaper och färdigheter såsom resultat på duggor",
	:exam_aids => "tillåtna hjälpmedel vid examination, samt om markeringar, indexeringar samt anteckningar i hjälpmedel är tillåtna,",
	:exam_time => "tid och plats för examination (ordinarie tentamenstillfälle)",
	:course_page => "Kurshemsida som kan nås från studentportalen"
}

def get_subject()
	"Påminnelse om kursPM"
end

def get_intro(examinator_first_name, course_code)
"Hej #{examinator_first_name},

Vi hoppas att allting är bra och att du ser fram emot din kurs kommande läsperiod.

Vi skriver för det snart är kursstart i kursen #{course_code}, och för att det enligt Chalmers föreskrifter för examination skall finnas ett komplett kurs-pm tillgängligt på kurshemsidan två veckor innan kursstart. Du kan läsa föreskrifterna här: #{TENTA_LINK} \n

Vi kan se att det saknas information om en del saker listat nedan.
"
end

def get_outro()
"Vi ser fram emot en intressant läsperiod, och vi kommer att göra vårt bästa för att hjälpa till så att kursen blir så bra som möjligt.\n

Ha en fortsatt trevlig dag

Med vänliga hälsningar
snIT - studienämnden på IT"
end

def get_parts(missing_parts)
	output = ""
	prefix = "   • "
	for p in missing_parts
		output = output + prefix + PARTS[p] + "\n"
	end
	output = output + "\n"
end

def get_missing_parts(row)
	missing_parts = []
	if row['kursens syfte och lärandemål'].nil?
		missing_parts.push(:purpose)
	end
	if row['examinator, föreläsare, övnings-/laborationshandledare, administrativ personal samt deras kontaktuppgifter'].nil?
		missing_parts.push(:examiner)
	end
	if row['kurslitteratur'].nil?
		missing_parts.push(:litterature)
	end
	if row['plan för föreläsningar, övningar och laborationer'].nil?
		missing_parts.push(:plan)
	end
	if row['en sammanfattning av gjorda förändringar sedan förra tillfälle'].nil?
		missing_parts.push(:changes)
	end
	if row['form för examinationen'].nil?
		missing_parts.push(:examination_form)
	end
	if row['betygsgränser och eventuella övriga krav för att bli godkänd på kursen (obligatoriska moment)'].nil?
		missing_parts.push(:grading_scale)
	end
	if row['hur obligatoriska moment bidrar till slutbetyget'].nil?
		missing_parts.push(:mandatory_parts)
	end
	if row['hur frivilliga moment bidrar till bedömningen av de studerandes kunskaper och färdigheter såsom resultat på duggor'].nil?
		missing_parts.push(:volentary_parts)
	end
	if row['tillåtna hjälpmedel vid examination, samt om markeringar, indexeringar samt anteckningar i hjälpmedel är tillåtna'].nil?
		missing_parts.push(:exam_aids)
	end
	if row['tid och plats för examination (ordinarie tentamenstillfälle)'].nil?
		missing_parts.push(:exam_time)
	end
	if row['kurshemsida'].nil?
		missing_parts.push(:course_page)
	end
	missing_parts

end

def send_email(examinator_email, examinator_first_name, course_code, missing_parts)
	# https://security.google.com/settings/security/apppasswords
	thePassword = 'yourAppPassword'

	Mail.defaults do
	       delivery_method :smtp, { :address              => "smtp.gmail.com",
	                                :port                 => 587,
	                                :domain               => 'chalmers.it',
	                                :user_name            => 'dr.horv@gmail.com',
	                                :password             => thePassword,
	                                :authentication       => 'plain',
	                                :enable_starttls_auto => true  }
	end

	body = get_intro(examinator_first_name, course_code) + get_parts(missing_parts) + get_outro()

	Mail.deliver do
	  from     'snit@chalmers.it'
	  to       examinator_email
	  bcc	   'snit@chalmers.it'
	  subject  get_subject()
	  body     body
	end
end

csv_text = File.read('data.csv')
csv = CSV.parse(csv_text, :headers => true)
csv.each do |row|
	missing_parts = get_missing_parts(row)
	course_code = row['kurs']
	examinator_first_name = row['Kursansvarig']
	examinator_email = row['email (examinator)']
	send_email(examinator_email, examinator_first_name, course_code, missing_parts)
end





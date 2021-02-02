# Contact data processor for Cléo
This is a simple python project which helped the company Cléo with their whatsapp contacts.

It organize the data in a common google contact csv, doing the following:

* Identify women (the target audience) by analysing the Brazil's data about names and respective genres

* Identify the probably main name of the person, walking through the words saved as the contact

* Exclude contacts without name or number

* Exclude contacts from state other than São Paulo (looking DDD's)

* Exclude contacts from country other than Brazil (looking DDI's)

* Exclude contacts which numbers cannot be a mobile phone

* Apply filters to let pass a contact or block it

* Assume a DDD and a DDI to contacts which gave not it

* Assume 8 digits numbers are old mobile phone numbers, and add a 9 to it

* Remove old telephony operator flags as '041', '015'

* Fix wrong DDD as '011' intead of '11'

* Exclude duplicates

* Uniforms the phone numbers

* Export the data to a csv file to be used after

Then was possible to use "WhatsWeb" chrome extension and send important messages automatically
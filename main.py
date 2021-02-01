from time import perf_counter
tic = perf_counter()

from csv import DictReader, writer, reader
from re import sub
from unicodedata import normalize


def encode(word):
    ascii_name = normalize("NFKD", word).encode("ascii", errors="ignore").decode("ascii")
    return ascii_name.upper()


def get_gender_data():
    with open('data/nomes.csv') as name_and_gender_file:
        name_and_gender_reader = DictReader(name_and_gender_file)
        return {line["first_name"]: line["classification"] for line in name_and_gender_reader}


def get_filters(filename):
    to_return = []
    with open(filename) as c:
        r = reader(c)
        for row in r:
            to_return.append(encode(row[0]))
        return to_return


pass_names = get_filters('filters/pass_names.csv')
block_names = get_filters('filters/block_names.csv')
blocked_numbers = get_filters('filters/blocked_numbers.csv')
blocked = []
passed = []

gender_data = get_gender_data()


def get_name_and_gender(person):
    encoded_names = encode(person).split()
    ng = None
    for n in encoded_names:
        if n in gender_data.keys():
            ng = n, gender_data[n]
            break
    if not ng:
        ng = encoded_names[0], 'F'
    if ng[0] in pass_names:
        ng = ng[0], 'F'
        passed.append([ng[0], person])
    elif ng[0] in block_names:
        ng = ng[0], 'M'
        blocked.append([ng[0], person])
    return ng


def deepcopy(li):
    return [v[:] for v in li]


def get_without_duplicates(data):
    data_copy = deepcopy(data)
    base = []
    for values in data:
        v = values[1]
        if v in base:
            for i, vc in enumerate(data_copy):
                if v in vc:
                    data_copy.pop(i)
                    break
        else:
            base.append(v)
    return data_copy


ddds = [str(n) for n in range(11, 20)]  # São Paulo DDDs

csv_file = open('data/contacts_google.csv')

csv_reader = DictReader(csv_file)

line_count = 0
new_data = []

for row in csv_reader:
    if line_count != 0:  # if its not the column title
        init = row['Name'], row['Phone 1 - Value']
        if init[0] and init[1]:  # if enough values
            first_name, gender = get_name_and_gender(init[0])
            if gender == 'F':  # if its probably a woman
                phones = [sub('[^0-9]', '', num) for num in init[1].split(' ::: ')]
                for phone in phones:
                    lenp = len(phone)
                    # 98174 3356
                    condition0 = lenp == 9
                    # 11 98174 3356
                    condition1 = lenp == 11 and phone[0:2] in ddds
                    # 55 11 98174 3356
                    condition2 = lenp == 13 and phone[0:2] == '55' and phone[2:4] in ddds
                    # 011 98174 3356
                    condition3 = lenp == 12 and phone[0] == '0' and phone[1:3] in ddds and phone[3] == '9'
                    # 041 11 98174 3356
                    condition4 = lenp == 14 and (phone[0:3] == '041' or phone[0:3] == '015') and phone[3:5] in ddds
                    # 8174 3356
                    condition5 = lenp == 8

                    # 041 8174 3356
                    condition6 = lenp == 11 and phone[0:3] == '041'
                    # 55 11 8174 3356
                    condition7 = lenp == 12 and phone[0:2] == '55' and phone[2:4] in ddds

                    # if a possible valid mobile phone of são paulo
                    if condition0 or condition1 or condition2 or condition3 or condition4 or condition5 or condition6 \
                            or condition7:
                        pre, pos = '', phone
                        if condition0:
                            pre = '5511'
                            # phone = ''.join(['5511', phone])
                        elif condition1:
                            pre = '55'
                            # phone = ''.join(['55', phone])
                        elif condition3:
                            pre, pos = '55', phone[1:]
                            # phone = ''.join(['55', phone[1:]])
                        elif condition4:
                            pre, pos = '55', phone[3:]
                            # phone = ''.join(['55', phone[3:]])
                        elif condition5:
                            pre = '55119'
                            # phone = ''.join(['55119', phone])
                        elif condition6:
                            pre, pos = '55119', phone[3:]
                            # phone = ''.join(['55119', phone[3:]])
                        elif condition7:
                            pre, pos = '55119', phone[4:]
                            # phone = ''.join(['55119', phone[4:]])

                        # add the needed info if the number didn't give it,
                        # assuming its a mobile phone with ddi 55 and ddd 11
                        phone = ''.join([pre, pos])

                        if phone not in blocked_numbers:
                            new_data.append([first_name, phone, init[0]])
    else:
        line_count += 1
csv_file.close()

without_duplicates = get_without_duplicates(new_data)

new_csv = open('output.csv', mode='w')
new_writer = writer(new_csv)

for line in without_duplicates:
    new_writer.writerow(line[:2])
new_csv.close()

toc = perf_counter()  # main file exported

# Debug and log

from tabulate import tabulate


if len(blocked) >= len(passed):
    table, to_add = deepcopy(blocked), passed
    first, second = 'Blocked', 'Passed'
else:
    table, to_add = deepcopy(passed), blocked
    first, second = 'Passed', 'Blocked'
for i, line in enumerate(table):
    if i < len(to_add):
        line.append(to_add[i][0])
        line.append(to_add[i][1])
table.insert(0, [first, f'{first} Original', second, f'{second} Original'])

before = len(new_data)
after = len(without_duplicates)
debug0 = f'New data has {after} entries. {before - after} duplicates was excluded and it took {toc - tic:0.4f} seconds'
debug1 = tabulate(without_duplicates, ('Name', 'Number', 'Original Name'), tablefmt="fancy_grid")
debug2 = tabulate(table, "firstrow", tablefmt="fancy_grid")
debugs = [debug0, debug1, debug2]

response, i = '', 0
while response != 'exit':
    print(debugs[i])
    i += 1 if i != len(debugs) - 1 else -i
    response = input()

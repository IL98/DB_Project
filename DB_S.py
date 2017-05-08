import re
import random
import numpy as np
import pandas as pd
import psycopg2

const = 20
cur_period = 0
exit = 0
next_l = 0

l = [0] * 20

def open_f(conn, s):
    cur = conn.cursor()
    f = open('%s' % s)
    n = []
    for i in f:
        n.append(tuple(re.findall(r'\S+\s\S+\s\S+|\S+\s\S+|\S\S+', i),))    
    f.close()
    if s == 'shareholders':
        cur.executemany("INSERT INTO shareholders (first_name, second_name) VALUES (%s, %s)", n)
    if s ==  'shares':
        cur.executemany("INSERT INTO shares (share_name, currency, total_quantity) VALUES (%s, %s, %s)", n)
    if s ==  'companies':
        cur.executemany("INSERT INTO companies VALUES (%s, %s, %s, %s)", n)
    conn.commit() 



def payback(conn):
    cur = conn.cursor()
    cur.execute("""SELECT shares.share_name, currency, total_quantity, net_income
    FROM shares
    INNER JOIN
    companies
    ON shares.share_name = companies.name;
    """)
    n = cur.fetchall()
    for i in n:
        a = round((float(i[1]) * float(i[2]) * 0.008)/(float(i[3]) * 1000000000), 2)
        cur.execute('UPDATE shares SET payback_raiting = %s WHERE share_name = %s ', (str(a), i[0]))
    conn.commit()    
    return    


def fund(conn):
    cur = conn.cursor()
    cur.execute('ALTER SEQUENCE shareholders_block_of_shares_seq RESTART;')
    cur.execute("SELECT currency, total_quantity FROM shares")
    n = cur.fetchall()
    for i in range(len(n)):
        a = round(0.5 * n[i][0]* n[i][1])
        cur.execute('UPDATE shareholders SET fund = %s WHERE block_of_shares = %s ', (str(a), str(i + 1)))
    conn.commit()
    return



def buy(d, i, conn):
    cur = conn.cursor()
    a = 0.5 * i[1]
    while 1:
        x = random.choice(d)
        s = round(a * random.uniform(0.1, 0.9), 2)
        delta = min(int(s / x[1]), round(0.6 * x[2]))
        a = a - int(delta * x[1])
        if delta == 0 or a <= 0 or s <= 0:
             break
        d.remove(x)
        x1 = list(x)
        x1[2] = x1[2] - delta 
        x1[3] = x1[3] +  delta        
        d.append(tuple(x1))
        cur.execute('UPDATE stock_exchange SET for_sale = %s, bought = %s WHERE share_name = %s', (str(x1[2]),str(x1[3]), x1[0]))
        cur.execute('SELECT * FROM shares_blocks WHERE block_id = %s AND share_name = %s', (str(i[0]), x1[0]))
        emp = cur.fetchall()
        if (len(emp) == 0):
            cur.execute('INSERT INTO shares_blocks VALUES (%s, %s, %s)', (str(i[0]), str(x[0]), str(delta)) )
        else:
            cur.execute('UPDATE shares_blocks SET quantity = %s WHERE block_id = %s AND share_name = %s', (str(emp[0][2] + delta), str(i[0]), x[0]))
    cur.execute('UPDATE shareholders SET fund = %s WHERE block_of_shares = %s ', (str(int(i[1] - 0.5 *i[1] + a)), str(i[0])))
    conn.commit()
    return
        

def game_begin(conn):
    cur = conn.cursor()
    cur.execute("SELECT block_of_shares, fund FROM shareholders")
    n = cur.fetchall()
    cur.execute("SELECT share_name, currency, for_sale, bought FROM stock_exchange")
    d = cur.fetchall()
    for i in n:
        buy(d, i, conn)
    conn.commit    
    return


def buy_in_game(conn):
    cur = conn.cursor()
    cur.execute("SELECT block_of_shares, fund FROM shareholders")
    n = cur.fetchall()
    cur.execute("SELECT share_name, currency, for_sale, bought FROM stock_exchange")
    d = cur.fetchall()
    x = random.randint(4, const)
    for k in range(x):
        i = random.choice(n)
        buy(d, i, conn)
    conn.commit()
    return
    
    
def list_to_list(l, d, index):
    c = len(d)
    for i in range(c):
        if (d[i][0] == index):
            l.append(d[i])
    return        
        


def sale(conn):
    cur = conn.cursor()
    cur.execute("SELECT share_name, currency, for_sale, sales   FROM stock_exchange")
    n = cur.fetchall()
    cur.execute("SELECT * FROM shares_blocks")
    d = cur.fetchall()
    cur.execute("SELECT * FROM shareholders")
    sh = cur.fetchall()
    x = random.randint(4, const)
    for i in range(x):
        one_person = random.randint(1,const)
        l_p = []
        list_to_list(l_p, d, one_person)
        if (len(l_p) != 0):
            r_p = random.randint(1, int(0.6 * len(l_p)))
            for j in range(r_p):
                x_p = random.choice(l_p)
                s = round(x_p[2] * random.uniform(0.1, 0.7))
                currency = [];
                list_to_list(currency, n, x_p[1])
                summ = round(s * currency[0][1])

                fun = []
                list_to_list(fun, sh, x_p[0])
            
                cur.execute('UPDATE shareholders SET fund = %s WHERE block_of_shares = %s', (str(fun[0][3] + summ), str(x_p[0])))  
            

                sh.remove(fun[0])
                fun1 = list(fun[0])
                fun1[3] = fun1[3] + summ
                sh.append(tuple(fun1))
            
                cur.execute('UPDATE stock_exchange SET sales = %s, for_sale = %s WHERE share_name = %s',(str(currency[0][3] + s), str(currency[0][2] + s), str(x_p[1]) ) )
            
   
                n.remove(currency[0])
                cur1 = list(currency[0])
                cur1[2]  = cur1[2] + s
                cur1[3] = cur1[3] + s
                n.append(tuple(cur1))
            
                cur.execute('UPDATE shares_blocks SET quantity = %s WHERE share_name = %s AND block_id = %s',
                       (str(x_p[2] - s), str(x_p[1]), str(x_p[0])) )

                d.remove(x_p)
                l_p.remove(x_p)
                x_p1 = list(x_p)
                x_p1[2] = x_p1[2] - s
                d.append(tuple(x_p1))
                l_p.append(tuple(x_p1))           
    conn.commit()
    return


def to_procent(a, b):
    x = 0
    if a == b:
        x = 0
        return x
    if (a != 0 and b == 0) or a/b >= 2:
        x = 100
        return x
    if 1 < a/b < 2 :
        x = round((a * 100 / b) % 100, 2 )
        return x
    if 0 < a/b < 1 :
        x = (-1) * round((a * 100 / b) % 100, 2)
        return x
    if a == 0 and b != 0:
        x =-100
        return x       


def update(conn):
    global cur_period
    cur = conn.cursor()
    cur.execute("SELECT *  FROM stock_exchange")
    n = cur.fetchall()
    for i in n:
        cur.execute('UPDATE stock_exchange SET demand_raiting = %s WHERE share_name = %s', 
                    (str(to_procent(i[3], i[5])), i[0] ) )
    
    cur.execute("SELECT * FROM shares WHERE period = %s", (str(cur_period)))
    n.clear()
    n  = cur.fetchall()
    for i in n:
        cur.execute("INSERT INTO shares VALUES (%s, %s, %s, %s, %s, %s, %s)", 
            (str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]), str(i[5]), str(i[6] + 1)))

    cur_period += 1
    
    cur.execute("SELECT demand_raiting  FROM stock_exchange")
    d = cur.fetchall();
    for i in range(len(n)) :
        currency = round(n[i][1] * (1 + float(n[i][2]) * random.uniform(-0.25, 1)/100 + (float(n[i][5])  * 6)/100 +  float(d[i][0])/400 ), 2)
        cur.execute('UPDATE shares SET currency = %s, upside_potential = %s WHERE share_name = %s AND  period = %s',
                     (str(currency), str(to_procent(currency, n[i][1])), str(n[i][0]), str(cur_period) ) )
                                                           
    n.clear()
                                                      
    if ((cur_period >= 5)):
        cur.execute("SELECT * FROM shares WHERE period = %s", (str(cur_period)))
        n  = cur.fetchall()                                                   
        cur.execute("SELECT * FROM shares WHERE period = %s", (str(cur_period - 5)))
        n1  = cur.fetchall()
        for i in range(len(n)):
            cur.execute('UPDATE shares SET one_year_change = %s WHERE period = %s AND share_name = %s', 
                        (str(n[i][1] - n1[i][1]), str(cur_period), str(n[i][0])) )
    x = cur_period - 6        
    cur.execute('DELETE FROM shares WHERE period = %s', (str(x), ) )                                                            
    
    
    conn.commit()    
    return


def perspective_shares(conn):
    cur = conn.cursor()
    cur.execute("""
    WITH A AS (SELECT upside_potential 
    FROM shares 
    WHERE  period = %s 
    ORDER BY  upside_potential DESC 
    LIMIT 1)
    SELECT share_name, A.upside_potential
    FROM shares
    INNER JOIN A
    ON shares.upside_potential = A.upside_potential
    WHERE period = %s
    """, (str(cur_period), str(cur_period)))
    n = cur.fetchall()
    cur.execute("""
    WITH A AS (SELECT payback_raiting 
    FROM shares 
    WHERE  period = %s 
    ORDER BY  payback_raiting DESC 
    LIMIT 1)
    SELECT share_name, A.payback_raiting
    FROM shares
    INNER JOIN A
    ON shares.payback_raiting = A.payback_raiting
    WHERE period = %s
    """, (str(cur_period), str(cur_period)))
    n1 = cur.fetchall()
    cur.execute("""
    WITH A AS (SELECT demand_raiting 
    FROM stock_exchange 
    ORDER BY  demand_raiting DESC 
    LIMIT 1)
    SELECT share_name, A.demand_raiting
    FROM stock_exchange 
    INNER JOIN A
    ON stock_exchange.demand_raiting = A.demand_raiting;
    """)
    n2 = cur.fetchall()
    print('The companies :')
    for i in n1:
        print(i[0],)
    print('have shares with one of the most profitable paybacks with a rating of :')
    print(n1[0][1])
    print('')
    
    print('The shares of the companies :')
    for i in n2:
        print(i[0],)
    print('have the largest demand rating on the exchange in size of :')
    print(n2[0][1])
    print('')
    
    print('The shares of the companies :')
    for i in n:
        print(i[0],)
    print('have the biggest increases in recent trading stocks rose in price :')
    print(n[0][1])
    return



def change_ind(conn, i):
    cur = conn.cursor()
    cur.execute("""
    WITH A AS (
       SELECT *
       FROM shares_blocks
       WHERE block_id = %s
    )
    SELECT quantity, currency
    FROM A
    INNER JOIN shares
    ON shares.share_name = A.share_name  AND shares.period = %s;
    """, (str(i), str(cur_period)) )
    n = cur.fetchall()
    x = 0
    for j in n:
        x += j[1]*j[0]
    cur.execute("""
    SELECT fund 
    FROM shareholders
    WHERE block_of_shares = %s
    """, (str(i), ))
    n = cur.fetchall()
    x += n[0][0]
    return round(x, 2)



def change_l(conn):
    global l
    for i in range(len(l)):
        l[i] = change_ind(conn, i + 1) - l[i]
    return

def max_l(conn):
    x = l.index(max(l)) + 1
    cur = conn.cursor()
    cur.execute("SELECT first_name, second_name FROM shareholders WHERE block_of_shares = %s", (str(x),))
    n = cur.fetchall()
    print('The most successful past trades turned out to be for %s %s he earned : %.2f' % (n[0][0], n[0][1], max(l)) )

    
def contr_holder(conn, s):
    cur = conn.cursor()
    cur.execute("SELECT name FROM companies")
    n = cur.fetchall()
    a = 0
    for i in n:
        if (i[0] == s):
            a = 1
            break
    if a == 0:
        print("incorrect argument")
        return
    cur.execute("""WITH A AS (SELECT * 
                FROM shares_blocks
                WHERE share_name = %s    
               ),
               B AS(
               SELECT * FROM shares
               WHERE share_name = %s AND period = %s
               ),
               C AS (SELECT A.share_name, block_id, quantity, total_quantity
               FROM A
               INNER JOIN B
               ON A.share_name = B.share_name)
               
               SELECT first_name, second_name
               FROM C
               INNER JOIN shareholders
               ON block_of_shares = block_id
               WHERE quantity >= 0.1 * total_quantity
            """, (s, s, str(cur_period)))
    n.clear()
    n = cur.fetchall()
    for i in n:
        print(i[0], i[1])
    return      
 
def print_table(conn, s):
    cur = conn.cursor()
    l = ['shares_blocks', 'shareholders', 'shares', 'stock_exchange', 'companies']
    if s not in l:
        print("incorrect name of table")
        return
        
    if s == 'shares_blocks':
        cur.execute("SELECT * FROM shares_blocks")
        n = cur.fetchall()
        print(pd.DataFrame(n, columns = ['block_id', 'share_name', 'quantity']))
    
    if s == 'shareholders':
        cur.execute("SELECT * FROM shareholders")
        n = cur.fetchall()
        print(pd.DataFrame(n, columns = ['block_of_shares', 'first_name', 'second_name', 'fund']))
    
    if s == 'shares':
        cur.execute("SELECT * FROM shares WHERE period = %s;", (str(cur_period), ))
        n = cur.fetchall()
        print(pd.DataFrame(n, columns = ['share_name', 'currency', 'upside_potential', 
                                         'one_year_change', 'total_quantity', 'payback_raiting', 'period']))    
    if s == 'stock_exchange':
        cur.execute("SELECT * FROM stock_exchange")
        n = cur.fetchall()
        print(pd.DataFrame(n, columns = ['sharedemand_raiting_name', 'currency', 'for_sale',
                                         'bought', 'demand_raiting', 'sales']))
    if s == 'companies':
        cur.execute("SELECT * FROM companies")
        n = cur.fetchall()
        print(pd.DataFrame(n, columns = ['name', 'ceo', 'total_assets', 'net_income']))
    return
    
    
def commandor(conn, l):
    if (l[0] == 'controlling' and l[1] == 'shareholder'):
        if (len(l) < 3):
            print("too few agruments")
        else:
            contr_holder(conn, l[2])
        return
    if (l[0] == 'most' and l[1] == 'successful' and l[2] == 'trader'):
        max_l(conn)
        return
    if (l[0] == 'reccomendations' and l[1] == 'for' and l[2] == 'purchase'):
        perspective_shares(conn)
        return
    if (l[0] == 'print'):
        if (len(l) < 2):
            print("too few agruments")
        else:
            print_table(conn, l[1])
        return    
    if (l[0] == 'next'):
        global next_l
        next_l = 1
        return
    if (l[0] == 'exit'):
        global exit
        exit = 1
        next_l = 1
        return
    print('not find this command, try again')
    return


def get_cur_per(conn):
    global cur_period
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT period FROM shares ORDER BY period DESC LIMIT 1')
    n = cur.fetchall()
    cur_period = n[0][0]
    return
    

def obnul(conn):
    cur = conn.cursor()
    cur.execute("UPDATE stock_exchange SET bought = 0, sales=0")
    conn.commit()
    


    
def full_rows_begin(conn):
    open_f(conn, 'companies')
    open_f(conn, 'shares')
    open_f(conn, 'shareholders')
    
    cur = conn.cursor()
    cur.execute("SELECT share_name, currency, total_quantity FROM shares")
    n = cur.fetchall()
    cur.executemany("INSERT INTO stock_exchange (share_name, currency, for_sale) VALUES (%s, %s, %s)", n)
    conn.commit()
    
    payback(conn)
    fund(conn)
    game_begin(conn)
    sale(conn)
    change_l(conn)
    update(conn)
    change_l(conn)
    return
     

def game(conn):
    obnul(conn)
    buy_in_game(conn)
    sale(conn)
    change_l(conn)
    update(conn)
    change_l(conn)
    return



conn = psycopg2.connect("dbname = 'postgres' user = 'postgres' password = '21esetef' host = 'localhost' port = 5432")


cur = conn.cursor()


get_cur_per(conn)


while exit != 1:
    next_l = 0
    while next_l != 1:
        print('enter the command :', )
        s = input()
        com_parse = re.findall(r'\w+', s)
        commandor(conn, com_parse)
    if exit == 1:
        break
    game(conn) 

   

print("ohh yeah")


conn.close()

CREATE TABLE shares_blocks(
  block_id int NOT NULL,
  share_name varchar(20) NOT NULL,
  quantity bigint DEFAULT 0,
  FOREIGN KEY (block_id) REFERENCES shareholders (block_of_shares)
);

CREATE TABLE shareholders(
  block_of_shares serial PRIMARY KEY,
  first_name varchar(15) NOT NULL,
  second_name varchar(15) NOT NULL,
  fund bigint DEFAULT 0
);

CREATE TABLE shares(
  share_name varchar(20)  NOT NULL,
  currency numeric(9,2)  NOT NULL,
  upside_potential float(2) DEFAULT 0,
  one_year_change float(2) DEFAULT 0,
  total_quantity  bigint NOT NULL,
  payback_raiting  float(2) DEFAULT 0,
  period int DEFAULT 0,

);

CREATE TABLE stock_exchange(
  share_name varchar(20) NOT NULL,
  currency float(2)  NOT NULL,
  for_sale bigint NOT NULL,
  bought bigint DEFAULT 0,
  demand_raiting float(2) DEFAULT 0,
  sales bigint DEFAULT 0,
    PRIMARY KEY (share_name) 
);

CREATE TABLE companies(
  name varchar(15) NOT NULL,
  ceo varchar(30) NOT NULL,
  total_assets float(2) NOT NULL,
  net_income float(2) NOT NULL,
  PRIMARY KEY (name) 
);

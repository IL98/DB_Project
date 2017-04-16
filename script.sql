CREATE TABLE Shares_Blocks(
  BLOCK_ID serial PRIMARY KEY,
  Share_name varchar(20) NOT NULL,
  Quantity bigint NOT NULL
);

CREATE TABLE ShareHolders(
  ID serial PRIMARY KEY,
  First_name varchar(15) NOT NULL,
  Second_name varchar(15) NOT NULL,
  Block_of_shares int NOT NULL,
  FUND bigint NOT NULL,
  FOREIGN KEY (Block_of_shares) REFERENCES Shares_Blocks (BLOCK_ID)
);

CREATE TABLE Shares(
  Share_name varchar(20)  NOT NULL,
  Currency numeric(7,2)  NOT NULL,
  Dividend numeric(2, 2)  NOT NULL,
  Upside_potential numeric(2, 2) NOT NULL,
  One_Year_Change float(2) NOT NULL,
  Total_quantity  bigint NOT NULL,
  PRIMARY KEY (Share_name) 
);

CREATE TABLE Stock_Exchange(
  Share_name varchar(20) NOT NULL,
  Currency numeric(7,2)  NOT NULL,
  For_Sale bigint NOT NULL,
  To_purchase bigint NOT NULL,
  Demand_raiting numeric(2, 2) NOT NULL,
  FOREIGN KEY (Share_name) REFERENCES Shares (Share_name)
);

CREATE TABLE Companies(
  Name varchar(15) NOT NULL,
  CEO varchar(30) NOT NULL,
  Revenue bigint NOT NULL,
  Total_equity bigint NOT NULL,
  Payback_raiting  numeric(2, 2) NOT NULL,
  PRIMARY KEY (Name) 
);

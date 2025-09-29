import pandas as pd
import psycopg2
import json
from datetime import datetime
from src.utils.logger import logger

class DatabaseLoader:
    def __init__(self, config_file="configs/db_config.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.connection = None
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.config)
            logger.info("Conectado ao PostgreSQL")
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise
    
    def create_tables(self):
        """Criar tabelas do Data Warehouse"""
        cursor = self.connection.cursor()
        
        # Dropar tabelas existentes para recriar com constraints
        cursor.execute("DROP TABLE IF EXISTS fato_hospedagem CASCADE")
        cursor.execute("DROP TABLE IF EXISTS dim_tempo CASCADE")
        cursor.execute("DROP TABLE IF EXISTS dim_hotel CASCADE")
        cursor.execute("DROP TABLE IF EXISTS dim_localizacao CASCADE")
        
        # Dim Tempo
        cursor.execute("""
            CREATE TABLE dim_tempo (
                sk_tempo SERIAL PRIMARY KEY,
                dia INTEGER,
                mes INTEGER,
                ano INTEGER,
                semana INTEGER,
                semestre INTEGER,
                UNIQUE(dia, mes, ano)
            )
        """)
        
        # Dim Hotel
        cursor.execute("""
            CREATE TABLE dim_hotel (
                sk_hotel SERIAL PRIMARY KEY,
                nome VARCHAR(255) UNIQUE,
                tipo VARCHAR(100),
                estrelas INTEGER
            )
        """)
        
        # Dim Localização
        cursor.execute("""
            CREATE TABLE dim_localizacao (
                sk_local SERIAL PRIMARY KEY,
                cidade VARCHAR(100),
                estado VARCHAR(100),
                pais VARCHAR(100),
                UNIQUE(cidade, estado, pais)
            )
        """)
        
        # Fato Hospedagem
        cursor.execute("""
            CREATE TABLE fato_hospedagem (
                sk_tempo INTEGER REFERENCES dim_tempo(sk_tempo),
                sk_hotel INTEGER REFERENCES dim_hotel(sk_hotel),
                sk_local INTEGER REFERENCES dim_localizacao(sk_local),
                preco DECIMAL(10,2),
                avaliacao DECIMAL(3,2)
            )
        """)
        
        self.connection.commit()
        logger.info("Tabelas criadas com sucesso")
    
    def load_data(self, csv_file):
        """Carregar dados do CSV para o DW"""
        df = pd.read_csv(csv_file)
        logger.info(f"Carregando {len(df)} registros de {csv_file}")
        
        # Processar cada linha
        for _, row in df.iterrows():
            try:
                # Extrair dados
                hotel_nome = row['title']
                endereco = row['address']
                preco_texto = row['final_price']
                avaliacao_texto = row['review_score']
                
                # Processar preço
                preco = self.extract_price(preco_texto)
                
                # Processar avaliação
                avaliacao = self.extract_rating(avaliacao_texto)
                
                # Processar localização
                cidade, estado, pais = self.parse_address(endereco)
                
                # Inserir dados
                self.insert_hotel_data(hotel_nome, preco, avaliacao, cidade, estado, pais)
                
            except Exception as e:
                logger.warning(f"Erro ao processar linha: {e}")
                continue
    
    def extract_price(self, price_text):
        """Extrair preço numérico do texto"""
        import re
        # Remove caracteres não numéricos exceto ponto e vírgula
        price_clean = re.sub(r'[^\d.,]', '', str(price_text))
        try:
            return float(price_clean.replace(',', '.'))
        except:
            return 0.0
    
    def extract_rating(self, rating_text):
        """Extrair avaliação numérica do texto"""
        import re
        # Procura por números no texto
        numbers = re.findall(r'\d+\.?\d*', str(rating_text))
        try:
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def parse_address(self, address):
        """Extrair cidade, estado, país do endereço"""
        # Exemplo: "Nakagyo Ward, Kyoto (Kawaramachi)"
        parts = address.split(',')
        if len(parts) >= 2:
            cidade = parts[1].strip().split('(')[0].strip()
            estado = parts[0].strip()
            pais = "Japan"  # Baseado no destino Kyoto Japan
        else:
            cidade = address
            estado = ""
            pais = "Japan"
        
        return cidade, estado, pais
    
    def insert_hotel_data(self, hotel_nome, preco, avaliacao, cidade, estado, pais):
        """Inserir dados do hotel no DW"""
        cursor = self.connection.cursor()
        
        try:
            # Inserir/obter sk_tempo (data atual)
            hoje = datetime.now()
            cursor.execute("""
                INSERT INTO dim_tempo (dia, mes, ano, semana, semestre)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (dia, mes, ano) DO NOTHING
            """, (hoje.day, hoje.month, hoje.year, hoje.isocalendar()[1], 1 if hoje.month <= 6 else 2))
            
            # Obter sk_tempo
            cursor.execute("""
                SELECT sk_tempo FROM dim_tempo 
                WHERE dia = %s AND mes = %s AND ano = %s
            """, (hoje.day, hoje.month, hoje.year))
            sk_tempo = cursor.fetchone()[0]
            
            # Inserir/obter sk_hotel
            cursor.execute("""
                INSERT INTO dim_hotel (nome, tipo, estrelas)
                VALUES (%s, %s, %s)
                ON CONFLICT (nome) DO NOTHING
            """, (hotel_nome, "Hotel", 0))
            
            # Obter sk_hotel
            cursor.execute("""
                SELECT sk_hotel FROM dim_hotel WHERE nome = %s
            """, (hotel_nome,))
            sk_hotel = cursor.fetchone()[0]
            
            # Inserir/obter sk_local
            cursor.execute("""
                INSERT INTO dim_localizacao (cidade, estado, pais)
                VALUES (%s, %s, %s)
                ON CONFLICT (cidade, estado, pais) DO NOTHING
            """, (cidade, estado, pais))
            
            # Obter sk_local
            cursor.execute("""
                SELECT sk_local FROM dim_localizacao 
                WHERE cidade = %s AND estado = %s AND pais = %s
            """, (cidade, estado, pais))
            sk_local = cursor.fetchone()[0]
            
            # Inserir fato
            cursor.execute("""
                INSERT INTO fato_hospedagem (sk_tempo, sk_hotel, sk_local, preco, avaliacao)
                VALUES (%s, %s, %s, %s, %s)
            """, (sk_tempo, sk_hotel, sk_local, preco, avaliacao))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Erro ao inserir dados: {e}")
            self.connection.rollback()
            raise
    
    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Conexão fechada")

if __name__ == "__main__":
    loader = DatabaseLoader()
    loader.connect()
    loader.create_tables()
    loader.load_data("data/interim/Kyoto_Japan_29-09-2025_15-21-09.csv")
    loader.close()
    print("Dados carregados com sucesso!")

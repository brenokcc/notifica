import os
import psycopg2
import psycopg2.extras
import datetime


def consulta_cpf(cpf):

    if not os.environ.get('ESUS_POSTGRES_PASSWORD'):
        return {}

    if os.environ.get('ESUS_POSTGRES_PASSWORD') == 'test':
        return MOCKED_DATA

    conn = psycopg2.connect(
    dbname=os.environ.get('ESUS_POSTGRES_DATABASE', 'esus'),
    user=os.environ.get('ESUS_POSTGRES_USER', 'esus_leitura'),
    password=os.environ.get('ESUS_POSTGRES_PASSWORD', 'QdvSO{6K1bDE3_3S-JFy1xEQvBR5zH'),
    host=os.environ.get('ESUS_POSTGRES_HOST', '10.10.10.219'),
    port=os.environ.get('ESUS_POSTGRES_PORT', '5433')
    )

    sql = """
    with
    stg_cpf_busca as (

    select '{cpf}'::text as cpf_busca -- Fabricio
    --select '04717379179'::text as cpf_busca
    --select '08655467111'::text as cpf_busca
    --select '00605219109'::text as cpf_busca  -- Robson

    )

   ,stg_csc_busca_co_cidadao as (

        select  tc.nu_cpf
              , max(tc.co_seq_cidadao) co_seq_cidadao

          from tb_cidadao tc

         where tc.st_ativo = 1
           and tc.dt_obito is null
           --and tc.nu_cpf is not null
           and tc.nu_cpf = (select cpf_busca from stg_cpf_busca )
         group by tc.nu_cpf

    )


    ,stg_parametros as (

        select tc.co_seq_cidadao
              ,tc.co_unico_ultima_ficha
              ,tc.dt_ultima_ficha
              ,pec.co_seq_fat_cidadao_pec

          from tb_cidadao tc

          inner join stg_csc_busca_co_cidadao stg
                  on stg.co_seq_cidadao = tc.co_seq_cidadao

           left join tb_fat_cidadao_pec pec
                  on pec.co_cidadao = tc.co_seq_cidadao

    )

    ,stg_fci_busca_ult_cns as (
    -- buscar a linha mais atual do nu_cns , particionado por co_fat_cidadao_pec

     select co_fat_cidadao_pec, co_dim_tempo, nu_cns, co_seq_fat_cad_individual
      from (
            SELECT
                co_fat_cidadao_pec,
                co_dim_tempo,
                nu_cns,
                co_seq_fat_cad_individual ,
                ROW_NUMBER() OVER (PARTITION BY co_fat_cidadao_pec ORDER BY co_dim_tempo DESC) as rn
            FROM tb_fat_cad_individual
              where length(nu_cns) > 1
                   and  co_fat_cidadao_pec in (select co_seq_fat_cidadao_pec from stg_parametros)
           )ranked
      where rn = 1

    )


    ,stg_csc_dados_individuo as (

        select --Dados do Individuo
               tc.co_seq_cidadao
              ,pec.co_seq_fat_cidadao_pec as co_fat_cidadao_pec
              ,tc.nu_cpf
              ,tc.nu_cns
              ,tc.no_cidadao
              ,tc.dt_nascimento
              ,tc.no_sexo
              --,tc.co_raca_cor
              ,trc.no_raca_cor                 as ds_raca_cor              -- CSC-0010-05: lookup operacional (FK real)
             -- ,tc.co_escolaridade
              ,tesc.no_escolaridade            as ds_dim_tipo_escolaridade -- CSC-0010-05: lookup operacional (FK real)
              ,tc.no_mae

              --Dados Residenciais
              ,null::text tp_logradouro
              ,tc.ds_logradouro
              ,tc.nu_numero
              ,tc.ds_complemento
              ,tc.no_bairro
              ,tc.ds_cep
              ,tl.no_localidade

              --Dados para Contato
              ,tc.nu_telefone_celular
              ,tc.ds_email
              --atualizado_ultimos_doze_meses=True

              ,case when tc.co_unico_ultima_ficha is not null
                        then true
                        else false
                end reg_fci
               ,tc.co_unico_ultima_ficha
               ,tc.dt_ultima_ficha
              ,case when tc.co_unico_ultima_ficha is not null
                        then
                            case when extract(year from age(current_date, tc.dt_ultima_ficha)) > 0
                                      then false
                                      else true
                             end

                        else  null
                end FCI_Atualizada

                ,tc.dt_atualizado
                ,tc.st_registro_cadsus
                ,tc.dt_atualizado_cadsus

          from tb_cidadao tc

          -- CSC-0010-05: tb_cidadao.co_raca_cor referencia tb_raca_cor (constraint fk_raca_cor_cidadao),
          --              não tb_dim_raca_cor. O join anterior trazia descrição errada ou nula.
          left join tb_raca_cor trc
                 on trc.co_raca_cor = tc.co_raca_cor

          -- CSC-0010-05: tb_cidadao.co_escolaridade referencia tb_escolaridade (constraint fk_escolaridade_cidadao).
          left join tb_escolaridade tesc
                 on tesc.co_escolaridade = tc.co_escolaridade

          left join tb_fat_cidadao_pec pec
                 on pec.co_cidadao = tc.co_seq_cidadao

          left join tb_localidade tl
                 on tl.co_localidade = tc.co_localidade_endereco

          where tc.co_seq_cidadao in (select co_seq_cidadao from stg_parametros)

    )


    ,stg_fci_dados_individuo as (

-------------------------------------------------------------------------------------
-- FICHA DE CADASTRO INDIVIDUAL
------------------------------------------------------------------------------------

        select tfci.co_seq_fat_cad_individual
              ,tfci.nu_cpf_cidadao
              ,tfci.nu_cns as nu_cns_fci
              ,ultcns.nu_cns as nu_cns_fci_ult
              ,tcci.no_cidadao
              ,tfci.dt_nascimento
              --,tfci.co_dim_sexo
              ,tds.ds_sexo
              --,tfci.co_dim_raca_cor
              ,tdrc.ds_raca_cor
              --,tfci.co_dim_tipo_escolaridade
              ,tdte.ds_dim_tipo_escolaridade
              ,tcci.no_mae_cidadao
              ,tcci.nu_celular_cidadao
              ,tcci.ds_email_cidadao
              ,tfci.co_dim_tempo
              ,tfci.nu_uuid_ficha

          from tb_fat_cad_individual tfci

          left join tb_cds_cad_individual tcci

                 on tcci.co_unico_ficha  = tfci.nu_uuid_ficha

          -- no ramo da FCI as colunas são co_dim_*: os joins com tb_dim_* estão corretos
          left join tb_dim_sexo tds
                 on tds.co_seq_dim_sexo  = tfci.co_dim_sexo

          left join tb_dim_raca_cor tdrc
                 on tdrc.co_seq_dim_raca_cor = tfci.co_dim_raca_cor

          left join tb_dim_tipo_escolaridade tdte
                 on tdte.co_seq_dim_tipo_escolaridade  = tfci.co_dim_tipo_escolaridade

          --ultimo cns do cidadao na FCI
          left join stg_fci_busca_ult_cns ultcns
                 on ultcns.co_fat_cidadao_pec = tfci.co_fat_cidadao_pec

         where tfci.nu_uuid_ficha in (select co_unico_ultima_ficha from stg_parametros)

    )

    ,stg_fcd_nucleo_familiar as (

        -------------------------------------------------------------------------------------
        -- NUCLEO FAMILIAR  (CSC-0010-05)
        -- Substitui a cadeia extinta tb_fat_familia_territorio -> tb_fat_cidadao_territorio.
        -- Sem filtro rígido de vínculo: ordena para que o vínculo vigente ganhe, mas mantém o
        -- vínculo antigo como última opção, para a tela não perder o endereço de quem se mudou.
        -------------------------------------------------------------------------------------

        select tcnf.co_cidadao
              ,tcnf.co_familia
              ,tf.co_cds_domicilio
              ,row_number() over ( partition by tcnf.co_cidadao
                                       order by tcnf.st_mudou_se asc
                                              , tf.st_domicilio_ativo desc
                                              , tf.st_familia_ainda_reside desc
                                              , tf.dt_atualizacao_fcd desc nulls last
                                              , tcnf.dt_ultima_atualizacao desc nulls last
                                 ) as rn

          from tb_cidadao_nucleo_familiar tcnf

          -- FK real: fk_cidnucleo_familia
          inner join tb_familia tf
                  on tf.co_seq_familia = tcnf.co_familia

         where tcnf.co_cidadao in (select co_seq_cidadao from stg_parametros)

    )

    ,stg_fcd_domicilio as (

        -- domicílio consolidado (1 linha por domicílio), já com o hash para achar a ficha
        select nf.co_cidadao
              ,tcd.co_seq_cds_domicilio
              ,tcd.co_unico_domicilio
              ,tcd.tp_logradouro
              ,tcd.no_logradouro
              ,tcd.nu_domicilio
              ,tcd.ds_complemento
              ,tcd.no_bairro
              ,tcd.ds_cep
              ,tcd.co_municipio
              ,tcd.nu_fone_referencia
              ,tcd.nu_latitude
              ,tcd.nu_longitude

          from stg_fcd_nucleo_familiar nf

          -- FK real: fk_cdsdomicilio_familia
          inner join tb_cds_domicilio tcd
                  on tcd.co_seq_cds_domicilio = nf.co_cds_domicilio

         where nf.rn = 1

    )

    ,stg_fcd_ficha_atual as (

        -- ficha de cadastro domiciliar mais recente do mesmo domicílio, só para preservar
        -- a coluna id_fcd_cds do contrato de saída
        select co_unico_domicilio
              ,co_seq_cds_cad_domiciliar

          from (
                select tccd.co_unico_domicilio
                      ,tccd.co_seq_cds_cad_domiciliar
                      ,row_number() over ( partition by tccd.co_unico_domicilio
                                               order by tccd.st_versao_atual desc nulls last
                                                      , tccd.dt_cad_domiciliar desc nulls last
                                         ) as rn
                  from tb_cds_cad_domiciliar tccd
                 where tccd.co_unico_domicilio in (select co_unico_domicilio from stg_fcd_domicilio)
               ) fichas

         where rn = 1

    )

    ,stg_fcd_dados_domicilio as (

        -------------------------------------------------------------------------------------
        -- DADOS DO DOMICILIO
        ------------------------------------------------------------------------------------

         select dom.co_cidadao                    as co_seq_cidadao
               ,dom.co_seq_cds_domicilio
               ,fch.co_seq_cds_cad_domiciliar

               -- CSC-0010-05: tb_cds_domicilio.tp_logradouro referencia tb_tipo_logradouro
               --              (constraint fk_tipologradouro_cdsdomicilio), não tb_dim_tipo_logradouro.
               ,ttl.no_tipo_logradouro            as ds_tipo_logradouro
               ,dom.no_logradouro
               ,dom.nu_domicilio
               ,dom.ds_complemento
               ,dom.no_bairro
               ,dom.ds_cep                        as nu_cep

               -- CSC-0010-05: tb_cds_domicilio.co_municipio referencia tb_localidade
               --              (constraint fk_localidade_cdsdomicilio), não tb_dim_municipio.
               ,tl.no_localidade                  as no_municipio

               -- Dados de Contato
               ,dom.nu_fone_referencia
               ,dom.nu_latitude
               ,dom.nu_longitude

           from stg_fcd_domicilio dom

           left join stg_fcd_ficha_atual fch
                  on fch.co_unico_domicilio = dom.co_unico_domicilio

           left join tb_localidade tl
                  on tl.co_localidade = dom.co_municipio

           left join tb_tipo_logradouro ttl
                  on ttl.co_tipo_logradouro = dom.tp_logradouro

    )

    ,stg_uniao_tab as (

        select  '||||||||||||||||||||||' as cadastro_simplificado

               ,tc.co_fat_cidadao_pec           as co_cidadao_pec
               ,tc.nu_cpf                       as csc_cpf
               ,tc.nu_cns                       as csc_cns
               ,tc.no_cidadao                   as csc_cidadao
               ,tc.dt_nascimento                as csc_dt_nascimento
               ,tc.no_sexo                      as csc_sexo
               ,tc.ds_raca_cor                  as csc_raca_cor
               ,tc.ds_dim_tipo_escolaridade     as csc_escolaridade
               ,tc.no_mae                       as csc_mae
               ,tc.tp_logradouro                as csc_tipo_logradouro
               ,tc.ds_logradouro                as csc_logradouro
               ,tc.nu_numero                    as csc_numero
               ,tc.ds_complemento               as csc_complemento
               ,tc.no_bairro                    as csc_bairro
               ,tc.ds_cep                       as csc_cep
               ,tc.no_localidade                as csc_localidade
               ,tc.nu_telefone_celular          as csc_celular
               ,tc.ds_email                     as csc_email
               ,tc.reg_fci                      as csc_reg_fci
               ,tc.co_unico_ultima_ficha        as csc_co_unico_ultima_ficha
               ,tc.dt_ultima_ficha              as csc_dt_ultima_ficha
               ,tc.fci_atualizada               as csc_fci_atualizada
               ,tc.dt_atualizado                as csc_dt_registro
               ,tc.st_registro_cadsus           as csc_registro_cadsus
               ,tc.dt_atualizado_cadsus         as csc_dt_atualizado_cadsus
               ,tc.co_fat_cidadao_pec           as csc_co_seq_fat_cidadao_pec
               ,tc.co_seq_cidadao               as csc_co_seq_cidadao

               ,'||||||||||||||||||||||' as ficha_fci
               ,fci.nu_cpf_cidadao              as fci_cpf
               ,fci.nu_cns_fci_ult              as fci_cns
               ,fci.no_cidadao                  as fci_cidadao
               ,fci.dt_nascimento               as fci_dt_nascimento
               ,fci.ds_sexo                     as fci_sexo
               ,fci.ds_raca_cor                 as fci_raca_cor
               ,fci.ds_dim_tipo_escolaridade    as fci_escolaridade
               ,fci.no_mae_cidadao              as fci_mae
               ,fci.nu_celular_cidadao          as fci_celular
               ,fci.ds_email_cidadao            as fci_email
               ,fci.co_dim_tempo                as fci_dt_registro
               ,fci.nu_uuid_ficha               as fci_nu_uuid_ficha
               ,fci.co_seq_fat_cad_individual   as fci_co_seq_fat_cad_individual

               ,'||||||||||||||||||||||' as ficha_fcd
               ,fcd.ds_tipo_logradouro          as fcd_tipo_logradouro
               ,fcd.no_logradouro               as fcd_logradouro
               ,fcd.nu_domicilio                as fcd_numero
               ,fcd.ds_complemento              as fcd_complemento
               ,fcd.no_bairro                   as fcd_bairro
               ,fcd.nu_cep                      as fcd_cep
               ,fcd.no_municipio                as fcd_municipio
               ,fcd.co_seq_cds_domicilio        as fcd_co_seq_cds_domicilio   -- CSC-0010-05: substitui fcd_co_seq_fat_cidadao_pec (uso interno)
               ,fcd.co_seq_cds_cad_domiciliar   as fcd_co_seq_cds_cad_domiciliar
               ,fcd.nu_latitude                 as fcd_latitude
               ,fcd.nu_longitude                as fcd_longitude

           from stg_csc_dados_individuo tc

           left join stg_fci_dados_individuo fci
                  on fci.nu_uuid_ficha = tc.co_unico_ultima_ficha

           -- CSC-0010-05: a amarração do domicílio passou a ser pelo co_seq_cidadao
           --              (antes era pelo co_fat_cidadao_pec, via tabelas de território)
           left join stg_fcd_dados_domicilio fcd
                  on fcd.co_seq_cidadao = tc.co_seq_cidadao

   )
     --select * from stg_uniao_tab
 ,tb_dados_cidadao as (

        select coalesce(fci_cpf, csc_cpf) as cpf
              ,coalesce(trim(fci_cns), csc_cns) as cns
              ,co_cidadao_pec
              ,coalesce(fci_cidadao, csc_cidadao) as cidadao
              ,coalesce(fci_dt_nascimento, csc_dt_nascimento) as dt_nascimento
              ,coalesce(fci_sexo, csc_sexo) as sexo
              ,coalesce(fci_raca_cor, csc_raca_cor) as raca_cor
              ,coalesce(fci_escolaridade, csc_escolaridade) as escolaridade
              ,coalesce(fci_mae, csc_mae) as mae
              ,coalesce(fci_celular, csc_celular) as celular
              ,coalesce(fci_email, csc_email) as email

              ,coalesce(fcd_tipo_logradouro, csc_tipo_logradouro) as tipo_logradouro
              ,coalesce(fcd_logradouro, csc_logradouro) as logradouro
              ,coalesce(fcd_numero, csc_numero) as numero
              ,coalesce(fcd_complemento, csc_complemento) as complemento
              ,coalesce(fcd_bairro, csc_bairro) as bairro
              ,coalesce(fcd_cep, csc_cep) as cep
              ,coalesce(fcd_municipio, csc_localidade) as municipio
              ,coalesce(fcd_latitude, null) as latitude
              ,coalesce(fcd_longitude, null) as longitude

              ,csc_reg_fci  as registro_fci
              ,csc_fci_atualizada as fci_atualizada
              ,csc_registro_cadsus as registro_cadsus
              ,csc_dt_atualizado_cadsus as dt_atualizado_cadsus

              ,csc_co_seq_cidadao as id_cidadao
              ,csc_co_seq_fat_cidadao_pec as id_cidadao_pec
              ,csc_co_unico_ultima_ficha as id_fci_ultima_ficha
              ,csc_dt_ultima_ficha as dt_ultima_ficha
              ,fci_co_seq_fat_cad_individual as id_fci
              ,fcd_co_seq_cds_cad_domiciliar as id_fcd_cds
              ,'CSC-0010-05' as query

          from stg_uniao_tab

   )

   select * from tb_dados_cidadao
    """.format(cpf=cpf.replace('.', '').replace('-', ''))


    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    print('ESUS', cpf, row)
    return row or {}


MOCKED_DATA = {
    "cpf": "81545711100",
    "cns": "0              ",
    "cidadao": "FABRICIO DA SILVA",
    "dt_nascimento": datetime.date(1977, 5, 26),
    "sexo": "Masculino",
    "raca_cor": "Branca",
    "escolaridade": "Superior, aperfeiçoamento, especialização, mestrado, doutorado",
    "mae": "ANGELA APARECIDA DE LOLLO SILVA",
    "celular": "19996917532",
    "email": "fa_bricio@msn.com",
    "tipo_logradouro": "1ª RUA",
    "logradouro": "RIO BRILHANTE",
    "numero": "285",
    "complemento": "ACS ELIANE",
    "bairro": "JARDIM SÃO PEDRO",
    "cep": "79810070",
    "municipio": "DOURADOS",
    "latitude": -22.2344696,
    "longitude": -54.805347,
    "registro_fci": True,
    "fci_atualizada": True,
    "registro_cadsus": 1,
    "dt_atualizado_cadsus": datetime.date(2020, 7, 13),
    "id_cidadao": 295168,
    "id_cidadao_pec": 1753595,
    "id_fci_ultima_ficha": "2710870-8b414969-6961-4ce7-888b-38c9ed50801f",
    "dt_ultima_ficha": datetime.date(2025, 1, 24),
    "id_fci": 4208805,
    "id_fcd_cds": 877040,
}
--
-- PostgreSQL database dump
--

\restrict gTDyEBIPHz3r5zaCruhfyt3x2npvLalI2EHVJfi8wsgC4CMCnHd8ju5WeAIiXvG

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: statut_jalon_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.statut_jalon_enum AS ENUM (
    'A_VENIR',
    'ACTUEL',
    'PASSE'
);


ALTER TYPE public.statut_jalon_enum OWNER TO postgres;

--
-- Name: statut_projet_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.statut_projet_enum AS ENUM (
    'EN_COURS',
    'PAS_COMMENCE',
    'BLOQUE',
    'STAND_BY',
    'TERMINE'
);


ALTER TYPE public.statut_projet_enum OWNER TO postgres;

--
-- Name: statut_tache_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.statut_tache_enum AS ENUM (
    'PAS_COMMENCE',
    'EN_COURS',
    'TERMINE',
    'BLOQUE',
    'STAND_BY'
);


ALTER TYPE public.statut_tache_enum OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    id_client integer NOT NULL,
    raison_sociale character varying(200) NOT NULL,
    mail_client character varying(150),
    telephone_client character varying(30),
    secteur character varying(100),
    date_dernier_contact date,
    latitude numeric(10,7),
    longitude numeric(10,7)
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- Name: clients_id_client_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clients_id_client_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clients_id_client_seq OWNER TO postgres;

--
-- Name: clients_id_client_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clients_id_client_seq OWNED BY public.clients.id_client;


--
-- Name: competences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competences (
    id_competence integer NOT NULL,
    nom_competence character varying(150) NOT NULL
);


ALTER TABLE public.competences OWNER TO postgres;

--
-- Name: competences_id_competence_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competences_id_competence_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.competences_id_competence_seq OWNER TO postgres;

--
-- Name: competences_id_competence_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competences_id_competence_seq OWNED BY public.competences.id_competence;


--
-- Name: conventions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conventions (
    id_convention integer NOT NULL,
    id_client integer NOT NULL,
    type_convention character varying(2) NOT NULL,
    date_debut_convention date NOT NULL,
    date_fin_convention date,
    regles text,
    cahier_charges text,
    prix numeric(10,2),
    convention character varying(255),
    bon_commande character varying(255),
    recap_mission character varying(255),
    CONSTRAINT convention_type_check CHECK (((type_convention)::text = ANY ((ARRAY['CE'::character varying, 'CC'::character varying])::text[])))
);


ALTER TABLE public.conventions OWNER TO postgres;

--
-- Name: conventions_id_convention_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conventions_id_convention_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conventions_id_convention_seq OWNER TO postgres;

--
-- Name: conventions_id_convention_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conventions_id_convention_seq OWNED BY public.conventions.id_convention;


--
-- Name: etats_relations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.etats_relations (
    id_etat_relation integer NOT NULL,
    libelle_relation character varying(150) NOT NULL
);


ALTER TABLE public.etats_relations OWNER TO postgres;

--
-- Name: etats_relations_id_etat_relation_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.etats_relations_id_etat_relation_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.etats_relations_id_etat_relation_seq OWNER TO postgres;

--
-- Name: etats_relations_id_etat_relation_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.etats_relations_id_etat_relation_seq OWNED BY public.etats_relations.id_etat_relation;


--
-- Name: interactions_client; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interactions_client (
    id_interaction integer NOT NULL,
    id_client integer NOT NULL,
    date_interaction date NOT NULL,
    detail_interaction text,
    id_etat_relation integer NOT NULL
);


ALTER TABLE public.interactions_client OWNER TO postgres;

--
-- Name: interactions_client_id_interaction_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interactions_client_id_interaction_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.interactions_client_id_interaction_seq OWNER TO postgres;

--
-- Name: interactions_client_id_interaction_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interactions_client_id_interaction_seq OWNED BY public.interactions_client.id_interaction;


--
-- Name: intervenant_competence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intervenant_competence (
    id_intervenant integer NOT NULL,
    id_competence integer NOT NULL,
    niveau_maitrise integer,
    CONSTRAINT check_niveau_maitrise CHECK (((niveau_maitrise >= 0) AND (niveau_maitrise <= 10)))
);


ALTER TABLE public.intervenant_competence OWNER TO postgres;

--
-- Name: intervenant_projet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intervenant_projet (
    id_intervenant integer NOT NULL,
    id_projet integer NOT NULL,
    date_debut_intervention date,
    date_fin_intervention date
);


ALTER TABLE public.intervenant_projet OWNER TO postgres;

--
-- Name: intervenant_tache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intervenant_tache (
    id_intervenant integer NOT NULL,
    id_tache integer NOT NULL
);


ALTER TABLE public.intervenant_tache OWNER TO postgres;

--
-- Name: intervenants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intervenants (
    id_intervenant integer NOT NULL,
    disponible boolean DEFAULT true NOT NULL,
    nb_heures_dispo integer,
    bulletin_adhesion character varying(255),
    carte_etudiante character varying(255),
    carte_vitale character varying(255),
    piece_identite character varying(255),
    photo_identite character varying(255),
    cv character varying(255)
);


ALTER TABLE public.intervenants OWNER TO postgres;

--
-- Name: jalons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jalons (
    id_jalon integer NOT NULL,
    id_projet integer NOT NULL,
    nom_jalon character varying(200) NOT NULL,
    statut_jalon public.statut_jalon_enum NOT NULL,
    date_debut_jalon date,
    date_fin_jalon date
);


ALTER TABLE public.jalons OWNER TO postgres;

--
-- Name: jalons_id_jalon_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jalons_id_jalon_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.jalons_id_jalon_seq OWNER TO postgres;

--
-- Name: jalons_id_jalon_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jalons_id_jalon_seq OWNED BY public.jalons.id_jalon;


--
-- Name: projet_competence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projet_competence (
    id_projet integer NOT NULL,
    id_competence integer NOT NULL
);


ALTER TABLE public.projet_competence OWNER TO postgres;

--
-- Name: projets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projets (
    id_projet integer NOT NULL,
    nom_projet character varying(200) NOT NULL,
    statut_projet public.statut_projet_enum NOT NULL,
    charge_projet integer,
    date_debut_projet date,
    date_fin_projet date,
    id_convention integer NOT NULL,
    convention character varying(255),
    bon_commande character varying(255),
    recap_mission character varying(255)
);


ALTER TABLE public.projets OWNER TO postgres;

--
-- Name: projets_id_projet_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projets_id_projet_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.projets_id_projet_seq OWNER TO postgres;

--
-- Name: projets_id_projet_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projets_id_projet_seq OWNED BY public.projets.id_projet;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id_role integer NOT NULL,
    nom_role character varying(100) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_role_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_role_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_role_seq OWNER TO postgres;

--
-- Name: roles_id_role_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_role_seq OWNED BY public.roles.id_role;


--
-- Name: taches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taches (
    id_tache integer NOT NULL,
    id_jalon integer NOT NULL,
    nom_tache character varying(200) NOT NULL,
    description_tache text,
    statut_tache public.statut_tache_enum NOT NULL,
    date_dernier_delai_tache date,
    id_intervenant_tache integer
);


ALTER TABLE public.taches OWNER TO postgres;

--
-- Name: taches_id_tache_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taches_id_tache_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taches_id_tache_seq OWNER TO postgres;

--
-- Name: taches_id_tache_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.taches_id_tache_seq OWNED BY public.taches.id_tache;


--
-- Name: utilisateurs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.utilisateurs (
    id_utilisateur integer NOT NULL,
    prenom_utilisateur character varying(100) NOT NULL,
    nom_utilisateur character varying(100) NOT NULL,
    mail_utilisateur character varying(150) NOT NULL,
    mdp_utilisateur character varying(255) NOT NULL,
    permission integer NOT NULL,
    id_role integer NOT NULL
);


ALTER TABLE public.utilisateurs OWNER TO postgres;

--
-- Name: utilisateurs_id_utilisateur_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.utilisateurs_id_utilisateur_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.utilisateurs_id_utilisateur_seq OWNER TO postgres;

--
-- Name: utilisateurs_id_utilisateur_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.utilisateurs_id_utilisateur_seq OWNED BY public.utilisateurs.id_utilisateur;


--
-- Name: clients id_client; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients ALTER COLUMN id_client SET DEFAULT nextval('public.clients_id_client_seq'::regclass);


--
-- Name: competences id_competence; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competences ALTER COLUMN id_competence SET DEFAULT nextval('public.competences_id_competence_seq'::regclass);


--
-- Name: conventions id_convention; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conventions ALTER COLUMN id_convention SET DEFAULT nextval('public.conventions_id_convention_seq'::regclass);


--
-- Name: etats_relations id_etat_relation; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.etats_relations ALTER COLUMN id_etat_relation SET DEFAULT nextval('public.etats_relations_id_etat_relation_seq'::regclass);


--
-- Name: interactions_client id_interaction; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions_client ALTER COLUMN id_interaction SET DEFAULT nextval('public.interactions_client_id_interaction_seq'::regclass);


--
-- Name: jalons id_jalon; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jalons ALTER COLUMN id_jalon SET DEFAULT nextval('public.jalons_id_jalon_seq'::regclass);


--
-- Name: projets id_projet; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projets ALTER COLUMN id_projet SET DEFAULT nextval('public.projets_id_projet_seq'::regclass);


--
-- Name: roles id_role; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id_role SET DEFAULT nextval('public.roles_id_role_seq'::regclass);


--
-- Name: taches id_tache; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taches ALTER COLUMN id_tache SET DEFAULT nextval('public.taches_id_tache_seq'::regclass);


--
-- Name: utilisateurs id_utilisateur; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateurs ALTER COLUMN id_utilisateur SET DEFAULT nextval('public.utilisateurs_id_utilisateur_seq'::regclass);


--
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clients (id_client, raison_sociale, mail_client, telephone_client, secteur, date_dernier_contact, latitude, longitude) FROM stdin;
\.


--
-- Data for Name: competences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competences (id_competence, nom_competence) FROM stdin;
\.


--
-- Data for Name: conventions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conventions (id_convention, id_client, type_convention, date_debut_convention, date_fin_convention, regles, cahier_charges, prix, convention, bon_commande, recap_mission) FROM stdin;
\.


--
-- Data for Name: etats_relations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.etats_relations (id_etat_relation, libelle_relation) FROM stdin;
1	Prospect
2	Client Actif
3	Ancien Client
\.


--
-- Data for Name: interactions_client; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interactions_client (id_interaction, id_client, date_interaction, detail_interaction, id_etat_relation) FROM stdin;
\.


--
-- Data for Name: intervenant_competence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.intervenant_competence (id_intervenant, id_competence, niveau_maitrise) FROM stdin;
\.


--
-- Data for Name: intervenant_projet; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.intervenant_projet (id_intervenant, id_projet, date_debut_intervention, date_fin_intervention) FROM stdin;
\.


--
-- Data for Name: intervenant_tache; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.intervenant_tache (id_intervenant, id_tache) FROM stdin;
\.


--
-- Data for Name: intervenants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.intervenants (id_intervenant, disponible, nb_heures_dispo, bulletin_adhesion, carte_etudiante, carte_vitale, piece_identite, photo_identite, cv) FROM stdin;
\.


--
-- Data for Name: jalons; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.jalons (id_jalon, id_projet, nom_jalon, statut_jalon, date_debut_jalon, date_fin_jalon) FROM stdin;
\.


--
-- Data for Name: projet_competence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projet_competence (id_projet, id_competence) FROM stdin;
\.


--
-- Data for Name: projets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projets (id_projet, nom_projet, statut_projet, charge_projet, date_debut_projet, date_fin_projet, id_convention, convention, bon_commande, recap_mission) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id_role, nom_role) FROM stdin;
1	Administrateur
2	Intervenant
\.


--
-- Data for Name: taches; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.taches (id_tache, id_jalon, nom_tache, description_tache, statut_tache, date_dernier_delai_tache, id_intervenant_tache) FROM stdin;
\.


--
-- Data for Name: utilisateurs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.utilisateurs (id_utilisateur, prenom_utilisateur, nom_utilisateur, mail_utilisateur, mdp_utilisateur, permission, id_role) FROM stdin;
1	Admin	Admin	admin	$2b$12$tgFWQzanVpp8MO9CGlV45ulmkjtPD2iSMmWN5RFRxzOAB1UAdvXeq	15	1
\.


--
-- Name: clients_id_client_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clients_id_client_seq', 1, false);


--
-- Name: competences_id_competence_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competences_id_competence_seq', 1, false);


--
-- Name: conventions_id_convention_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.conventions_id_convention_seq', 1, false);


--
-- Name: etats_relations_id_etat_relation_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.etats_relations_id_etat_relation_seq', 3, true);


--
-- Name: interactions_client_id_interaction_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interactions_client_id_interaction_seq', 1, false);


--
-- Name: jalons_id_jalon_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.jalons_id_jalon_seq', 1, false);


--
-- Name: projets_id_projet_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projets_id_projet_seq', 1, false);


--
-- Name: roles_id_role_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_role_seq', 2, true);


--
-- Name: taches_id_tache_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.taches_id_tache_seq', 1, false);


--
-- Name: utilisateurs_id_utilisateur_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.utilisateurs_id_utilisateur_seq', 1, true);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id_client);


--
-- Name: competences competences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competences
    ADD CONSTRAINT competences_pkey PRIMARY KEY (id_competence);


--
-- Name: conventions conventions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conventions
    ADD CONSTRAINT conventions_pkey PRIMARY KEY (id_convention);


--
-- Name: etats_relations etats_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.etats_relations
    ADD CONSTRAINT etats_relations_pkey PRIMARY KEY (id_etat_relation);


--
-- Name: interactions_client interactions_client_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions_client
    ADD CONSTRAINT interactions_client_pkey PRIMARY KEY (id_interaction);


--
-- Name: intervenant_competence intervenant_competence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_competence
    ADD CONSTRAINT intervenant_competence_pkey PRIMARY KEY (id_intervenant, id_competence);


--
-- Name: intervenant_projet intervenant_projet_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_projet
    ADD CONSTRAINT intervenant_projet_pkey PRIMARY KEY (id_intervenant, id_projet);


--
-- Name: intervenant_tache intervenant_tache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_tache
    ADD CONSTRAINT intervenant_tache_pkey PRIMARY KEY (id_intervenant, id_tache);


--
-- Name: intervenants intervenants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenants
    ADD CONSTRAINT intervenants_pkey PRIMARY KEY (id_intervenant);


--
-- Name: jalons jalons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jalons
    ADD CONSTRAINT jalons_pkey PRIMARY KEY (id_jalon);


--
-- Name: projet_competence projet_competence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projet_competence
    ADD CONSTRAINT projet_competence_pkey PRIMARY KEY (id_projet, id_competence);


--
-- Name: projets projets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projets
    ADD CONSTRAINT projets_pkey PRIMARY KEY (id_projet);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_role);


--
-- Name: taches taches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taches
    ADD CONSTRAINT taches_pkey PRIMARY KEY (id_tache);


--
-- Name: utilisateurs utilisateurs_mail_utilisateur_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_mail_utilisateur_key UNIQUE (mail_utilisateur);


--
-- Name: utilisateurs utilisateurs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_pkey PRIMARY KEY (id_utilisateur);


--
-- Name: conventions conventions_id_client_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conventions
    ADD CONSTRAINT conventions_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client);


--
-- Name: interactions_client interactions_client_id_client_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions_client
    ADD CONSTRAINT interactions_client_id_client_fkey FOREIGN KEY (id_client) REFERENCES public.clients(id_client) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: interactions_client interactions_client_id_etat_relation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interactions_client
    ADD CONSTRAINT interactions_client_id_etat_relation_fkey FOREIGN KEY (id_etat_relation) REFERENCES public.etats_relations(id_etat_relation) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: intervenant_competence intervenant_competence_id_competence_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_competence
    ADD CONSTRAINT intervenant_competence_id_competence_fkey FOREIGN KEY (id_competence) REFERENCES public.competences(id_competence) ON DELETE CASCADE;


--
-- Name: intervenant_competence intervenant_competence_id_intervenant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_competence
    ADD CONSTRAINT intervenant_competence_id_intervenant_fkey FOREIGN KEY (id_intervenant) REFERENCES public.intervenants(id_intervenant) ON DELETE CASCADE;


--
-- Name: intervenant_projet intervenant_projet_id_intervenant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_projet
    ADD CONSTRAINT intervenant_projet_id_intervenant_fkey FOREIGN KEY (id_intervenant) REFERENCES public.intervenants(id_intervenant) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: intervenant_projet intervenant_projet_id_projet_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_projet
    ADD CONSTRAINT intervenant_projet_id_projet_fkey FOREIGN KEY (id_projet) REFERENCES public.projets(id_projet) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: intervenant_tache intervenant_tache_id_intervenant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_tache
    ADD CONSTRAINT intervenant_tache_id_intervenant_fkey FOREIGN KEY (id_intervenant) REFERENCES public.intervenants(id_intervenant) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: intervenant_tache intervenant_tache_id_tache_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenant_tache
    ADD CONSTRAINT intervenant_tache_id_tache_fkey FOREIGN KEY (id_tache) REFERENCES public.taches(id_tache) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: intervenants intervenants_id_intervenant_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intervenants
    ADD CONSTRAINT intervenants_id_intervenant_fkey FOREIGN KEY (id_intervenant) REFERENCES public.utilisateurs(id_utilisateur) ON DELETE CASCADE;


--
-- Name: jalons jalons_id_projet_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jalons
    ADD CONSTRAINT jalons_id_projet_fkey FOREIGN KEY (id_projet) REFERENCES public.projets(id_projet) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: projet_competence projet_competence_id_competence_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projet_competence
    ADD CONSTRAINT projet_competence_id_competence_fkey FOREIGN KEY (id_competence) REFERENCES public.competences(id_competence) ON DELETE CASCADE;


--
-- Name: projet_competence projet_competence_id_projet_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projet_competence
    ADD CONSTRAINT projet_competence_id_projet_fkey FOREIGN KEY (id_projet) REFERENCES public.projets(id_projet) ON DELETE CASCADE;


--
-- Name: projets projets_id_convention_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projets
    ADD CONSTRAINT projets_id_convention_fkey FOREIGN KEY (id_convention) REFERENCES public.conventions(id_convention);


--
-- Name: taches taches_id_intervenant_tache_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taches
    ADD CONSTRAINT taches_id_intervenant_tache_fkey FOREIGN KEY (id_intervenant_tache) REFERENCES public.intervenants(id_intervenant) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: taches taches_id_jalon_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taches
    ADD CONSTRAINT taches_id_jalon_fkey FOREIGN KEY (id_jalon) REFERENCES public.jalons(id_jalon) ON DELETE CASCADE;


--
-- Name: utilisateurs utilisateurs_id_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.utilisateurs
    ADD CONSTRAINT utilisateurs_id_role_fkey FOREIGN KEY (id_role) REFERENCES public.roles(id_role);


--
-- PostgreSQL database dump complete
--

\unrestrict gTDyEBIPHz3r5zaCruhfyt3x2npvLalI2EHVJfi8wsgC4CMCnHd8ju5WeAIiXvG


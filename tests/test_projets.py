import pytest
from datetime import date   
from app.models import db, Projet

def test_liste_projets_empty(projet):
    response = projet.get("/projets/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Projets" in html

def test_ajouter_projet_is_right_page(projet):
    pass

def test_ajouter_projet_post(projet, app):
    pass

def test_ajouter_projet_post_missing_field(projet, app):
    pass

def test_ajouter_projet_duplicate(projet, app):
    pass

def test_details_projet(projet, app):
    pass

def test_details_projet_404(projet):
    pass

def test_modifier_projet_deadline_7_jan(projet):
    pass
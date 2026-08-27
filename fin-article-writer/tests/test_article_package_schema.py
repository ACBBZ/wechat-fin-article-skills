import json
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / 'references' / 'article-package.schema.json'


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding='utf-8'))


def test_schema_requires_v3_style_and_semantic_anchors():
    schema = load_schema()
    required = set(schema['required'])
    assert 'style' in required
    assert 'section_anchors' in required

    anchors = schema['properties']['section_anchors']
    assert anchors['minItems'] == 3
    assert {'id', 'purpose'} <= set(anchors['items']['required'])


def test_schema_enforces_3000_to_3600_visible_chars():
    schema = load_schema()
    article = schema['properties']['article']
    assert 'visible_char_count' in article['required']
    visible = article['properties']['visible_char_count']
    assert visible['minimum'] == 3000
    assert visible['maximum'] == 3600


def test_schema_requires_three_auto_insert_images_with_anchor_ids():
    schema = load_schema()
    images = schema['properties']['images']
    assert images['minItems'] == 3
    assert images['minContains'] == 3
    assert 'anchor_id' in images['items']['properties']
    assert 'anchor_id' in images['contains']['required']

    roles = set(images['items']['properties']['role']['enum'])
    assert 'mechanism_explainer' in roles
    assert 'explanatory_visual' in roles


def test_cover_schema_carries_style_reference():
    schema = load_schema()
    cover = schema['properties']['cover']
    assert 'style_reference' in cover['required']
    style_reference = cover['properties']['style_reference']
    assert style_reference['type'] == 'object'

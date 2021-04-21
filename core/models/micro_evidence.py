"micro evidence"
from django.db import models
from .micro_knowledge import MicroKnowledge, MICRO_EVIDENCE


class MicroEvidence(MicroKnowledge):
    """micro evidenve

    Fields:
        - citations: cited paper
        - source: url of this paper
        - published_year: when the paper published
    """
    citation = models.CharField(max_length=200)
    source = models.URLField()
    published_year = models.IntegerField()

    def to_hash(self):
        rst = dict()
        tags = list(self.tag_list.values('id', 'name', 'type'))
        rst.update({
            "id": self.id,
            "created_by": {
                "id": self.created_by.id,
                "icon": str(self.created_by.icon),
                "username": self.created_by.username,
                "institution": self.created_by.institution,
            },
            "tags": tags,
            "content": self.content,
            "judge_status": self.judge_status,
            "citation": self.citation,
            "source": self.source,
            "published_year": self.published_year,
            "created_at": self.created_at,
            "favor_num": self.favorites_num(),
            "like_num": self.like_num(),
            "type": self.micro_type(),
        })
        return rst

    def micro_type(self):
        return MICRO_EVIDENCE

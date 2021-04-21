"micro conjecture"
from django.db import models
from .micro_knowledge import MicroKnowledge, MICRO_CONJECTURE
from .micro_evidence import MicroEvidence


class MicroConjecture(MicroKnowledge):
    """micro evidenve

    Fields:
        - citations: cited paper
        - source: url of this paper
        - published_year: when the paper published
    """
    evidences = models.ManyToManyField(to=MicroEvidence)

    def to_hash(self):
        rst = dict()
        tags = list(self.tag_list.values('id', 'name', 'type'))
        evidences_json_list = []
        for evidence in self.evidences.values():
            ob = MicroEvidence.objects.get(pk=evidence.get('id'))
            evidences_json_list.append(ob.to_hash())
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
            "evidences": evidences_json_list,

            "created_at": self.created_at,
            "favor_num": self.favorites_num(),
            "like_num": self.like_num(),
            "type": self.micro_type(),
        })
        return rst

    def micro_type(self):
        return MICRO_CONJECTURE

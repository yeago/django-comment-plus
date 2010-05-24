from django import template
from django.template.loader import render_to_string
from django.db.models import Count
from django.contrib.comments.templatetags.comments import BaseCommentNode, CommentFormNode

register = template.Library()

class KarmaCommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs.annotate(Count('karma')).order_by('-karma__count'))

def get_karma_comment_list(parser, token):
    return KarmaCommentListNode.handle_token(parser, token)

register.tag(get_karma_comment_list)

class RenderCommentStageNode(CommentFormNode):
    """Render the comment strage directly"""

    #@classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_comment_stage and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_form for obj %}
        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

        # {% render_comment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype = BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr = parser.compile_filter(tokens[3])
            )
    handle_token = classmethod(handle_token)

    def render(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
	print self.object_expr.resolve(context)
        if object_pk:
            template_search_list = [
                "comments/%s/%s/stage.html" % (ctype.app_label, ctype.model),
                "comments/%s/stage.html" % ctype.app_label,
                "comments/stage.html"
            ]
            context.push()
            stagestr = render_to_string(template_search_list, {"object" : self.object_expr.resolve(context)}, context)
            context.pop()
            return stagestr
        else:
            return ''

def render_comment_stage(parser, token):
	return RenderCommentStageNode.handle_token(parser, token)

register.tag(render_comment_stage)

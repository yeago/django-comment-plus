from django import template
from django.template.loader import render_to_string
from django.db.models import Count
from django.db.models.query import QuerySet
from django.contrib.comments.templatetags.comments import BaseCommentNode, CommentFormNode

register = template.Library()


class RemoveCommentNode(template.Node):
    def __init__(self, user, object, var_name):
        self.user = template.Variable(user)
        self.object = template.Variable(object)
        self.var_name = var_name

    def render(self, context):
        object = self.object.resolve(context)
        user = self.user.resolve(context)
        var = self.var_name
        if hasattr(object, 'comment_remove_by'):
            if object.comment_remove_by(user):
                context[var] = True
        return ''


def set_comment_remove_variable(parser, token):
    args = token.split_contents()
    if not len(args) in [4, 6]:
        raise template.TemplateSyntaxError("Not the right amount of args")

    return RemoveCommentNode(args[2], args[3], args[5])

register.tag(set_comment_remove_variable)


class KarmaCommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs.annotate(Count('karma')))


def get_karma_comment_list(parser, token):
    return KarmaCommentListNode.handle_token(parser, token)

register.tag(get_karma_comment_list)


class RenderCommentStageNode(CommentFormNode):
    """Render the comment strage directly"""
    def __init__(self, qs=None, *args, **kwargs):
        self.explicit_varname = qs
        super(RenderCommentStageNode, self).__init__(*args, **kwargs)

    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse render_comment_stage and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        # {% render_comment_form for obj %}
        if len(tokens) == 3 or (len(tokens) == 5 and tokens[3] == 'with'):
            qs = None
            if len(tokens) == 5:
                qs = parser.compile_filter(tokens[4])
            return cls(object_expr=parser.compile_filter(tokens[2]), qs=qs)

        # {% render_comment_form for app.models pk %}
        elif len(tokens) == 4:
            return cls(
                ctype=BaseCommentNode.lookup_content_type(tokens[2], tokens[0]),
                object_pk_expr=parser.compile_filter(tokens[3])
            )

    def render(self, context, template_search_list=None):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if object_pk:
            defaults = [
                "comments/%s/%s/stage.html" % (ctype.app_label, ctype.model),
                "comments/%s/stage.html" % ctype.app_label,
                "comments/stage.html"
            ]
            template_search_list = template_search_list or defaults
            context.push()

            render_context = {
                "request": context.get("request"),
                "object": self.object_expr.resolve(context),
            }

            if self.explicit_varname:
                render_context['comment_list'] = self.explicit_varname.resolve(context)

            stagestr = render_to_string(
                template_search_list,
                render_context,
                context)
            context.pop()
            return stagestr
        return ''


def render_comment_stage(parser, token):
    return RenderCommentStageNode.handle_token(parser, token)

register.tag(render_comment_stage)

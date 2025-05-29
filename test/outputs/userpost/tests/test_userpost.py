"""Integration tests for the generated userpost package."""

import datetime

# These imports assume that the 'userpost' package (in test/outputs/userpost)
# is discoverable by pytest, e.g., by running pytest from test/outputs/
# or by having test/outputs in PYTHONPATH.

from userpost.gen.models import (
    User,
    TextPost,
    ImagePost,
    Post,
    Role,
    Node,
    PostBase,
    SearchResult,
)
from userpost.gen import auto as userpost_auto


def test_union_aliases():
    """Test that union aliases work correctly and are accepted by type checkers."""
    # Create concrete post instances
    text_post = TextPost(
        id="1",
        title="Test Text Post",
        author=User(
            id="user1",
            username="testuser",
            role=Role.USER,
        ),
        content="This is a test post.",
    )

    image_post = ImagePost(
        id="2",
        title="Test Image Post",
        author=User(
            id="user2",
            username="photographer",
            role=Role.USER,
        ),
        imageUrl="https://example.com/image.jpg",
        caption="A beautiful image",
    )

    # Test that union alias exists and accepts concrete types
    post_1: Post = text_post
    post_2: Post = image_post

    # Verify the types are preserved
    assert isinstance(post_1, TextPost)
    assert isinstance(post_2, ImagePost)
    assert post_1.title == "Test Text Post"
    assert post_2.imageUrl == "https://example.com/image.jpg"


def test_interface_inheritance():
    """Test that interface inheritance works correctly with field validation."""
    # Test that TextPost inherits from PostBase which implements Node
    text_post = TextPost(
        id="post123",
        title="Inherited Fields Test",
        author=User(
            id="author1",
            username="writer",
            role=Role.ADMIN,
        ),
        content="Testing interface inheritance",
    )

    # Assert inherited fields from PostBase (which implements Node)
    assert hasattr(text_post, "id")
    assert hasattr(text_post, "title")
    assert hasattr(text_post, "author")
    assert text_post.id == "post123"
    assert text_post.title == "Inherited Fields Test"

    # Test actual inheritance relationships
    assert issubclass(TextPost, PostBase)
    assert issubclass(PostBase, Node)
    assert isinstance(text_post, PostBase)
    assert isinstance(text_post, Node)


def test_forward_reference_in_union():
    """Test that forward references in unions resolve correctly after model rebuild."""
    # Create a User with a favourite Post (forward reference)
    user = User(
        id="user1",
        username="postlover",
        role=Role.USER,
    )

    # Create a TextPost that references the User
    text_post = TextPost(
        id="post1",
        title="Forward Reference Test",
        author=user,
        content="Testing forward references",
    )

    # Update the user to reference the post (circular reference)
    user.favouritePost = text_post

    # Verify the relationships work
    assert user.favouritePost is not None
    assert user.favouritePost.id == "post1"
    assert text_post.author.id == "user1"

    # Test that the union types resolve correctly
    post_union: Post = text_post
    search_result: SearchResult = user

    assert isinstance(post_union, TextPost)
    assert isinstance(search_result, User)

    # Test model validation with circular references (exclude the circular field)
    user_dict = user.model_dump(exclude={"favouritePost"})
    reconstructed_user = User.model_validate(user_dict)
    assert reconstructed_user.id == "user1"
    assert reconstructed_user.username == "postlover"


def test_enum_and_custom_scalars():
    """Test enum fields and custom scalar type mappings."""
    # Test enum usage
    admin_user = User(
        id="admin1",
        username="administrator",
        role=Role.ADMIN,  # Test enum field
        lastLogin=datetime.datetime.now(),  # Test custom scalar DateTime (fixed deprecation)
    )

    guest_user = User(
        id="guest1",
        username="visitor",
        role=Role.GUEST,
        lastLogin=datetime.datetime(2024, 1, 1, 12, 0, 0),
    )

    # Verify enum values
    assert admin_user.role == Role.ADMIN
    assert guest_user.role == Role.GUEST
    assert admin_user.role.value == "ADMIN"
    assert guest_user.role.value == "GUEST"

    # Test all enum values exist
    assert hasattr(Role, "ADMIN")
    assert hasattr(Role, "USER")
    assert hasattr(Role, "GUEST")

    # Verify custom scalar types work
    assert isinstance(admin_user.lastLogin, datetime.datetime)
    assert isinstance(guest_user.lastLogin, datetime.datetime)

    # Test enum is properly typed
    assert issubclass(Role, str)  # Role extends str
    assert isinstance(Role.ADMIN, str)  # Enum values are strings


# Additional helper test to verify package structure
def test_userpost_package_structure():
    """Test that core components of the userpost package are available."""
    # Test that mixins are available if needed
    assert hasattr(userpost_auto, "register_compute_fn")
    assert hasattr(userpost_auto, "register_expand_fn")

    # Test that models are properly imported
    from userpost.gen import models as userpost_models_module

    assert "User" in dir(userpost_models_module)
    assert "Post" in dir(userpost_models_module)
    assert "Role" in dir(userpost_models_module)
    assert "TextPost" in dir(userpost_models_module)
    assert "ImagePost" in dir(userpost_models_module)
    assert "VideoPost" in dir(userpost_models_module)

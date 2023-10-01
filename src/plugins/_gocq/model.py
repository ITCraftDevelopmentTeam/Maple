from typing import TypeAlias, Literal, TypedDict


UserId: TypeAlias = str | int
GroupId: TypeAlias = str | int
MessageId: TypeAlias = str | int
Message: TypeAlias = str
Sex = Literal['male', 'female', 'unknown']
GroupRole = Literal['owner', 'admin', 'member']
RecordFormat = Literal['mp3', 'amr', 'wma', 'm4a', 'spx', 'ogg', 'wav', 'flac']
HonorType = Literal[
    'talkative',        # 龙王
    'performer',        # 群聊之火
    'legend',           # 群聊炽焰
    'strong_newbie',    # 冒尖小春笋
    'emotion'           # 快乐之源
]


class Variant(TypedDict):
    model_show: str
    need_pay: bool


class Device(TypedDict):
    app_id: int
    device_name: str
    device_kind: str


class User(TypedDict):
    user_id: int
    nickname: str


class Stranger(User):
    sex: Sex
    age: int
    qid: str
    level: int
    login_days: int


class Friend(User):
    remark: str


class UnidirectionalFriend(User):
    source: str


class BaseMessage(TypedDict):
    message_id: int
    real_id: int
    message_type: Literal['private', 'group']
    sender: User
    time: int
    message: Message
    raw_message: Message


class PrivateMessage(BaseMessage):
    group: Literal[False]


class GroupMessage(BaseMessage):
    group: Literal[True]
    group_id: int


class ForwardNodeInfo(TypedDict):
    content: Message
    sender: User
    time: int


class ReferenceForwardData(TypedDict):
    id: MessageId


class CustomForwardNodeData(TypedDict, total=False):
    name: str
    uin: int
    content: Message | list['ForwardNode']
    seq: Message
    time: int


class ForwardNode(TypedDict):
    type: Literal['node']
    data: ReferenceForwardData | CustomForwardNodeData


class ForwardMessage(TypedDict):
    message_id: int
    forward_id: str


class Image(TypedDict):
    size: int
    filename: str
    url: str


class TextDetection(TypedDict):
    text: str
    confidence: int
    coordinates: list[tuple[int, int]]


class OCR(TypedDict):
    texts: list[TextDetection]
    language: str


class GroupInfo(TypedDict):
    group_id: int
    group_name: str
    group_memo: str
    group_create_time: int
    group_level: int
    member_count: int
    max_member_count: int


class GroupMember(User):
    group_id: int
    card: str
    sex: Sex
    age: int
    join_time: int
    last_sent_time: int
    level: str
    role: GroupRole
    unfriendly: bool
    card_changeable: bool
    shut_up_timestamp: int


class RichGroupMember(GroupMember):
    area: str
    title: str
    title_expire_time: int


class BaseHonored(User):
    avatar: str


class Honored(BaseHonored):
    description: str


class CurrentTalkative(BaseHonored):
    day_count: int


class AllHonors(TypedDict):
    group_id: int
    current_talkative: CurrentTalkative
    talkative_list: list[Honored]
    performer_list: list[Honored]
    legend_list: list[Honored]
    strong_newbie_list: list[Honored]
    emotion_list: list[Honored]


class BaseRequest(TypedDict):
    request_id: int
    group_id: int
    group_name: str
    checked: bool
    actor: int


class InvitedRequest(BaseRequest):
    invitor_uin: int
    invitor_nick: str


class JoinRequest(BaseRequest):
    requester_uin: int
    requester_nick: str
    message: str


class GroupSystemMessage(TypedDict):
    invited_requests: list['InvitedRequest']
    join_requests: list['JoinRequest']


class EssenceMessage(TypedDict):
    sender_id: int
    sender_nick: str
    sender_time: int
    operator_id: int
    operator_nick: str
    operator_time: int
    message_id: int


class GroupAtAllRemain(TypedDict):
    can_at_all: bool
    remain_at_all_count_for_group: int
    remain_at_all_count_for_uin: int


class Anonymous(TypedDict):
    id: int
    name: str
    flag: str


class GroupNoticeImage(TypedDict):
    height: str
    width: str
    id: str


class GroupNoticeMessage(TypedDict):
    text: str
    images: list[GroupNoticeImage]


class GroupNotice(TypedDict):
    sender_id: int
    publish_time: int
    message: GroupNoticeMessage


class File(TypedDict):
    group_id: int
    file_id: str
    file_name: str
    busid: int
    file_size: int
    upload_time: int
    dead_time: int
    modify_time: int
    download_times: int
    uploader: int
    uploader_name: str


class Folder(TypedDict):
    group_id: int
    folder_id: str
    folder_name: str
    create_time: int
    creator: int
    creator_name: str
    total_file_count: int


class GroupFileSystemInfo(TypedDict):
    file_count: int
    limit_count: int
    used_space: int
    total_space: int


class GroupFolderInfo(TypedDict):
    files: list[File]
    folders: list[Folder]


class Credentials(TypedDict):
    cookies: str
    csrf_token: int


VersionInfo = TypedDict('VersionInfo', {
    'app_name': Literal['go-cqhttp'],
    'app_version': str,
    'app_full_name': str,
    'protocol_name': Literal[6],
    'protocol_version': Literal['v11'],
    'coolq_edition': Literal['pro'],
    'coolq_directory': str,
    'go-cqhttp': Literal[True],
    'plugin_version': Literal['4.15.0'],
    'plugin_build_number': Literal[99],
    'plugin_build_configuration': Literal['release'],
    'runtime_version': str,
    'runtime_os': str,
    'version': str
})


class Statistics(TypedDict):
    packet_received: int
    packet_sent: int
    packet_lost: int
    message_received: int
    message_sent: int
    disconnect_times: int
    lost_times: int
    last_message_time: int


class Status(TypedDict):
    app_initialized: Literal[True]
    app_enabled: Literal[True]
    plugins_good: Literal[True]
    app_good: Literal[True]
    online: bool
    good: bool
    stat: Statistics


def custom_forward_node(
    name: str,
    uin: UserId,
    content: Message | list[ForwardNode],
    time: int
) -> ForwardNode:
    return ForwardNode(
        type='node',
        data=CustomForwardNodeData(
            name=name,
            uin=int(uin),
            content=content,
            time=time
        )
    )


def reference_forward_node(id: Message) -> ForwardNode:
    return ForwardNode(type='node', data=ReferenceForwardData(id=id))

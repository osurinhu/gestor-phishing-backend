from datetime import datetime, date, time
from ext.database import db
from sqlalchemy import BigInteger, ForeignKey, Text, String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    created_group: Mapped[List['Group']] = relationship(back_populates='creator')
    created_target: Mapped[List['Target']] = relationship(back_populates='creator')
    created_template: Mapped[List['Template']] = relationship(back_populates='creator')
    created_campaign: Mapped[List['Campaign']] = relationship(back_populates='creator')

class Group(db.Model):
    __tablename__ = 'group'

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(200), default='')
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    creator: Mapped['User'] = relationship(back_populates='created_group')
    group_member: Mapped[List['Target']] = relationship(back_populates='in_group')
    group_campaign: Mapped[List['Campaign']] = relationship(back_populates='group')

class Target(db.Model):
    __tablename__ = 'target'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id'))
    creator_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String(50))
    person_code: Mapped[str] = mapped_column(String(25))
    email: Mapped[str] = mapped_column(String(255))
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    creator: Mapped['User'] = relationship(back_populates='created_target')
    in_group: Mapped['Group'] = relationship(back_populates='group_member')
    email_received: Mapped[List['EmailSent']] = relationship(back_populates='target')


class Template(db.Model):
    __tablename__ = 'template'

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    creator_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(200), default='')
    code: Mapped[str] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationship
    creator: Mapped['User'] = relationship(back_populates='created_template')
    template_campaign: Mapped[List['Campaign']] = relationship(back_populates='template')

class Campaign(db.Model):
    __tablename__ = 'campaign'

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('user.id'))
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id'))
    template_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey('template.id'))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(200), default='')
    sender_email: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(1), default='i')
    start_date: Mapped[date] = mapped_column()
    end_date: Mapped[date] = mapped_column()
    send_time: Mapped[time] = mapped_column()
    subject_text: Mapped[str] = mapped_column(String(50))
    title_text: Mapped[str] = mapped_column(String(50))
    button_text: Mapped[str] = mapped_column(String(50))
    body_text: Mapped[str] = mapped_column(String(500))
    deleted: Mapped[bool] = mapped_column(default=False)

    # Relationship
    creator: Mapped['User'] = relationship(back_populates='created_campaign')
    group: Mapped['Group'] = relationship(back_populates='group_campaign')
    template: Mapped['Template'] = relationship(back_populates='template_campaign')
    email_sent: Mapped[List['EmailSent']] = relationship(back_populates='from_campaign')

class EmailSent(db.Model):
    __tablename__ = 'email_sent'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey('target.id'))
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaign.id'))
    interacted: Mapped[bool] = mapped_column(default=False)
    interaction_date: Mapped[Optional[datetime]] = mapped_column()

    # Relationship
    target: Mapped['Target'] = relationship(back_populates='email_received')
    from_campaign: Mapped['Campaign'] = relationship(back_populates='email_sent')
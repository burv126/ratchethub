"""Campaign message templates by type."""

from __future__ import annotations

from app.marketing.enums import CampaignType, Channel

# {name}, {vehicle}, {service}, {shop}, {offer}
TEMPLATES: dict[CampaignType, dict[Channel, str]] = {
    CampaignType.MAINTENANCE_REMINDER: {
        Channel.SMS: (
            'Здравствуйте, {name}! Возможно, вашему {vehicle} требуется {service}. Записать вас в {shop}? Ответьте YES для записи.'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nДля вашего {vehicle} подходит срок обслуживания: {service}. Хотим напомнить об этом заранее.\nОтветьте, и мы подберём удобное время.\nВсего доброго,\n{shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Это {shop}. Вашему {vehicle} требуется {service}. Нажмите 1 для разговора с консультантом и выбора удобного времени.'
        ),
    },
    CampaignType.DECLINED_ESTIMATE: {
        Channel.SMS: (
            'Здравствуйте, {name}! Мы готовы помочь с услугой {service} для вашего {vehicle}, когда вам будет удобно. Ответьте YES, если хотите обсудить варианты.'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nРешение о работах {service} для вашего {vehicle} может быть непростым. Мы готовы предложить варианты и ответить на вопросы.\nОтветьте, если хотите вернуться к смете.\nС уважением,\n{shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Это {shop}. Хотим уточнить ваш интерес к смете на {service} для вашего {vehicle}. Нажмите 1, чтобы спокойно обсудить варианты.'
        ),
    },
    CampaignType.THANK_YOU: {
        Channel.SMS: (
            'Здравствуйте, {name}! Спасибо за визит в {shop}. Были рады помочь — безопасных дорог!'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nСпасибо, что доверили автомобиль {shop}. Надеемся, теперь всё в порядке.\nЕсли понадобится помощь, просто напишите.\n— Команда {shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Это {shop}. Спасибо за визит и доверие. Хорошего дня!'
        ),
    },
    CampaignType.REVIEW_REQUEST: {
        Channel.SMS: (
            'Здравствуйте, {name}! Надеемся, после визита всё в порядке. Будем рады вашему отзыву о {shop}: {offer}'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nНадеемся, вы довольны обслуживанием. Ваш отзыв поможет нам стать лучше.\nБудем благодарны, если найдёте минуту для отзыва: {offer}\nСпасибо,\n{shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Это {shop}. Надеемся, ваш визит прошёл хорошо. Будем благодарны за короткий отзыв.'
        ),
    },
    CampaignType.SEASONAL_PROMOTION: {
        Channel.SMS: (
            'Здравствуйте, {name}! Сезонное предложение от {shop}: {offer}. Ответьте YES, и мы подберём удобное время.'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nНовое сезонное предложение от {shop}:\n{offer}\nКогда вам будет удобно, будем рады записать вас.\nДо встречи,\n{shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Это {shop} с сезонным предложением: {offer}. Нажмите 1 для записи.'
        ),
    },
    CampaignType.RECALL_NOTICE: {
        Channel.SMS: (
            'Здравствуйте, {name}! Ваш {vehicle} может подпадать под отзывную кампанию. {shop} поможет провести проверку. Ответьте YES для записи.'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nВаш {vehicle} может подпадать под отзывную кампанию. Мы поможем провести проверку без лишних хлопот.\nЗапишитесь на осмотр в {shop}, когда сможете. Ваша безопасность важнее всего.\n— {shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Важная информация от {shop} о безопасности вашего {vehicle}. Нажмите 1, чтобы записаться на проверку.'
        ),
    },
    CampaignType.BIRTHDAY: {
        Channel.SMS: (
            'С днём рождения, {name}! Желаем прекрасного дня. Подарок от команды {shop}: {offer}'
        ),
        Channel.EMAIL: (
            'С днём рождения, {name}!\nКоманда {shop} желает вам всего самого доброго. Примите наш подарок: {offer}\nС праздником!'
        ),
        Channel.VOICE: (
            'С днём рождения, {name}! Команда {shop} желает вам прекрасного дня. {offer}'
        ),
    },
    CampaignType.INACTIVE_CUSTOMER: {
        Channel.SMS: (
            'Здравствуйте, {name}! Давно не виделись в {shop}. Будем рады вам — на этой неделе предлагаем бесплатный осмотр вашего автомобиля. Ответьте YES для записи.'
        ),
        Channel.EMAIL: (
            'Здравствуйте, {name}!\nДавно не виделись в {shop}. Понимаем, что забот хватает. Будем рады видеть вас снова и предлагаем бесплатный комплексный осмотр: {offer}\nДо встречи!\n{shop}'
        ),
        Channel.VOICE: (
            'Здравствуйте, {name}! Это {shop}. Будем рады видеть вас снова. Нажмите 1, чтобы записаться на бесплатный осмотр.'
        ),
    },
}

EMAIL_SUBJECTS: dict[CampaignType, str] = {
    CampaignType.MAINTENANCE_REMINDER: 'Напоминание об обслуживании автомобиля',
    CampaignType.DECLINED_ESTIMATE: 'Готовы помочь, когда вам удобно',
    CampaignType.THANK_YOU: 'Спасибо за доверие',
    CampaignType.REVIEW_REQUEST: 'Как прошло обслуживание? Поделитесь отзывом',
    CampaignType.SEASONAL_PROMOTION: 'Сезонное предложение',
    CampaignType.RECALL_NOTICE: 'Информация о безопасности автомобиля',
    CampaignType.BIRTHDAY: 'С днём рождения от нашей команды',
    CampaignType.INACTIVE_CUSTOMER: 'Будем рады видеть вас снова',
}


def render_template(
    campaign_type: CampaignType,
    channel: Channel,
    *,
    name: str = "there",
    vehicle: str = "vehicle",
    service: str = "service",
    shop: str = 'наш автосервис',
    offer: str = 'специальное предложение',
    custom: str | None = None,
) -> str:
    if custom:
        return custom.format(
            name=name, vehicle=vehicle, service=service, shop=shop, offer=offer
        )
    tmpl = TEMPLATES[campaign_type][channel]
    return tmpl.format(name=name, vehicle=vehicle, service=service, shop=shop, offer=offer)

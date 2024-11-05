from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, Application
from datetime import datetime, timedelta
import os

# Этапы диалога
DOCUMENTS, EXAMINATIONS, PARENT_DOCUMENTS, CONFIRMATION = range(4)

# Перечень необходимых данных
required_documents = {
    "Направление на госпитализацию": "до 14 дней",
    "Выписка из амбулаторной карты (форма № 027/у)": "актуально",
    "Справка об отсутствии контактов с инфекционными больными": "до 3 дней",
    "Бактериологическое обследование (до 3 лет)": "до 14 дней",
    "Анализ на гельминтозы и протозоозы": "до 14 дней",
    "ЭКГ": "до 30 дней",
    "Клинический анализ крови": "до 10 дней",
    "Анализ мочи": "до 10 дней",
    "Группа крови и резус-фактор": "до 10 дней",
    "Гепатит В и С (ИФА)": "до 30 дней",
    "Флюорограмма (старше 15 лет)": "до 1 года",
    "Свидетельство о рождении/паспорт": "актуально",
    "Полис и СНИЛС": "актуально"
}

parent_documents = {
    "Флюорографическое обследование": "до 1 года",
    "Анализ на сифилис": "до 21 дня",
    "Сертификат прививок или иммунитет к кори": "актуально",
}

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Здравствуйте! Я помогу вам проверить наличие всех необходимых документов для госпитализации.\n"
        "Сначала проверим основные документы. Пожалуйста, напишите 'да', если документ есть, и 'нет', если его нет.\n"
        f"1. {list(required_documents.keys())[0]}, {list(required_documents.values())[0]}"
    )
    context.user_data['document_index'] = 0
    context.user_data['missing_documents'] = []
    return DOCUMENTS

async def check_documents(update: Update, context: CallbackContext) -> int:
    answer = update.message.text.lower()
    index = context.user_data['document_index']
    document_name = list(required_documents.keys())[index]
    
    if answer == 'да':
        pass    
    
    elif answer == 'нет':
        context.user_data['missing_documents'].append(document_name)

    else:
        await update.message.reply_text(f"Ошибка. Ответьте ДА или НЕТ. {context.user_data['document_index'] + 1}. {list(required_documents.keys())[context.user_data['document_index']]}")
        return DOCUMENTS    
        
    context.user_data['document_index'] += 1
    
    if context.user_data['document_index'] < len(required_documents):
        next_document = list(required_documents.keys())[context.user_data['document_index']]
        await update.message.reply_text(f"{context.user_data['document_index'] + 1}. {next_document}")
        return DOCUMENTS
    else:
        await update.message.reply_text(
            "Теперь проверим документы, необходимые для родителей. Напишите 'да' или 'нет'.\n"
            f"1. {list(parent_documents.keys())[0]}"
        )
        context.user_data['parent_index'] = 0
        return PARENT_DOCUMENTS

async def check_parent_documents(update: Update, context: CallbackContext) -> int:
    answer = update.message.text.lower()
    index = context.user_data['parent_index']
    document_name = list(parent_documents.keys())[index]
    
    if answer == 'да':
        pass
    
    elif answer == 'нет':
        context.user_data['missing_documents'].append(document_name)
        
    else:
        await update.message.reply_text(f"Ошибка. Ответьте ДА или НЕТ. {context.user_data['document_index'] + 1}. {list(parent_documents.keys())[context.user_data['parent_index']]}")
        return PARENT_DOCUMENTS

    context.user_data['parent_index'] += 1
    if context.user_data['parent_index'] < len(parent_documents):
        next_document = list(parent_documents.keys())[context.user_data['parent_index']]
        await update.message.reply_text(f"{context.user_data['parent_index'] + 1}. {next_document}")
        return PARENT_DOCUMENTS
    else:
        missing_docs = context.user_data['missing_documents']
        if missing_docs:
           await update.message.reply_text(f"Не хватает следующих документов и обследований: {', '.join(missing_docs)}")
        else:
           await update.message.reply_text("Все необходимые документы собраны!")
        
        await update.message.reply_text("Спасибо за использование бота. Желаем успешной госпитализации!")
        return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Операция отменена. Будем рады помочь вам снова.")
    return ConversationHandler.END

def main():
    # Create the application and pass it your bot's token.
    application = Application.builder().token(os.environ.get('token')).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DOCUMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_documents)],
            PARENT_DOCUMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_parent_documents)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # on different commands - answer in Telegram
    #application.add_handler(CommandHandler("start", start))
    #application.add_handler(CommandHandler("check_documents", check_documents))
    #application.add_handler(CommandHandler("check_parent_documents", check_parent_documents))
    #application.add_handler(CommandHandler("cancel", cancel))
    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(conv_handler) 
  

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tools.notification import NotificationStates, Notification
from tools.tools import is_admin

dp = Router()
@dp.message(Command("send_notification"))
async def cmd_send_notification(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("📝 Введите текст уведомления:")
        await state.set_state(NotificationStates.waiting_for_text)
    else:
        await message.answer("Недостаточно прав")


@dp.message(NotificationStates.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    if len(message.text) > 4000:
        await message.answer("⚠️ Текст уведомления слишком длинный. Максимум 4000 символов.")
        return

    await state.update_data(text=message.text)

    builder = InlineKeyboardBuilder()
    for level in range(1, 5):
        builder.button(text=f"Уровень {level}", callback_data=f"notif_level_{level}")
    builder.button(text="❌ Отмена", callback_data="notif_cancel")
    builder.adjust(2, repeat=True)

    await message.answer(
        "🔢 Выберите уровень уведомления (1-4):",
        reply_markup=builder.as_markup()
    )
    await state.set_state(NotificationStates.waiting_for_level)


@dp.callback_query(F.data.startswith("notif_level_"), NotificationStates.waiting_for_level)
async def process_level(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    level = int(callback.data.split('_')[2])
    data = await state.get_data()

    try:
        notification = Notification(text=data['text'], notification_class=level, bot=bot)
        await notification.send_notification()
        await callback.message.edit_text("✅ Уведомление успешно отправлено!")
    except Exception as e:
        await callback.message.edit_text(f"⚠️ Ошибка при отправке: {str(e)}")

    await state.clear()



@dp.callback_query(F.data == "notif_cancel", NotificationStates.waiting_for_level)
async def cancel_notification(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отправка уведомления отменена")


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("❌ Действие отменено")
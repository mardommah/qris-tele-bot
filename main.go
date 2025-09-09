package main

import (
	"context"
	"log"
	"os"
	"os/signal"

	"github.com/go-telegram/bot"
	"github.com/go-telegram/bot/models"
	"github.com/joho/godotenv"
)

// Send any text message to the bot after the bot has been started

func main() {

	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	botKey := os.Getenv("BOT_TOKEN")

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	opts := []bot.Option{
		bot.WithDefaultHandler(handler),
	}

	b, err := bot.New(botKey, opts...)
	if err != nil {
		panic(err)
	}

	b.Start(ctx)
}

func handler(ctx context.Context, b *bot.Bot, update *models.Update) {
	// Hanya tangani command /start
	if update.Message != nil && update.Message.Text == "/start" {
		_, err := b.SendMessage(ctx, &bot.SendMessageParams{
			ChatID: update.Message.Chat.ID,
			Text:   "👋 Halo, selamat datang di bot saya!\n\nKetik /help untuk melihat perintah yang tersedia.",
		})
		if err != nil {
			log.Println("Gagal kirim pesan:", err)
		}
	}
}

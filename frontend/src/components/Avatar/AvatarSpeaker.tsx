// @ts-ignore - Bypasses the missing type declaration error for the .mjs file
import { TalkingHead } from "./talkinghead/talkinghead.mjs";

export class AvatarSpeaker {
  // 1. We must declare class properties in TypeScript
  container: HTMLElement;
  head: any;

  // 2. We define 'container' as an HTML element
  constructor(container: HTMLElement) {
    this.container = container;
    this.head = null;
  }

  // Initialize the TalkingHead instance and load the avatar model
  async init() {
    this.head = new TalkingHead(this.container, {
      lipsyncModules: ["en"],
      cameraView: "head",
      cameraX: -0.15,
      cameraY: 0.3,
      cameraDistance: 0.3,
    });

    await this.head.showAvatar({
      // The URL of the avatar model to load（you can change to other model）
      // set up lip sync language to English
      url: "/avatars/avaturn.glb",
      body: "F",
      avatarMood: "neutral",
      lipsyncLang: "en",
    });
  }


  // Speak the given text using the avatar's voice and lipsync, using the TTS API to generate speech audioc
  async speak(text: string, languageCode = "en-US") {
    if (!this.head) {
      throw new Error("AvatarSpeaker has not been initialized.");
    }
    if (!text || !text.trim()) {
      return;
    }

    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

    const response = await fetch(`${apiUrl}/tts/tts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        language_code: languageCode,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to synthesize speech.");
    }

    const data = await response.json();

    const audioBytes = Uint8Array.from(
        atob(data.audio),
        (char) => char.charCodeAt(0)
    );

    const audioContext = new AudioContext();

    const audioBuffer = await audioContext.decodeAudioData(
        audioBytes.buffer
    );

    // 4. We tell TypeScript that 'word' is an object containing any data
    const words = data.words.map((word: any) => word.value);
    const wordTimes = data.words.map((word: any) => word.time);

    // 5. We define 'time' and 'index' as numbers
    const wordDurations = wordTimes.map((time: number, index: number) => {
      if (index < wordTimes.length - 1) {
        return wordTimes[index + 1] - time;
      }

      return audioBuffer.duration * 1000 - time;
    });

    this.head.speakAudio(
        {
          audio: audioBuffer,
          words: words,
          wtimes: wordTimes,
          wdurations: wordDurations,
        },
        {
          lipsyncLang: "en",
        }
    );
  }

  // Dispose of the TalkingHead instance and clean up resources
  dispose() {
    if (this.head) {
      this.head.dispose();
      this.head = null;
    }
    if (this.container) {
      this.container.innerHTML = "";
    }
  }
}
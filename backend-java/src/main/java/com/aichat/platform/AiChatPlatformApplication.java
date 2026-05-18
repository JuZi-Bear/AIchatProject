package com.aichat.platform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class AiChatPlatformApplication {

    public static void main(String[] args) {
        SpringApplication.run(AiChatPlatformApplication.class, args);
    }
}

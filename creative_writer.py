"""
Creative Writing and Personalization Module

This module provides creative content generation with tone adaptation
and A/B testing capabilities.
"""

import logging
import random
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class WritingTone(Enum):
    """Available writing tones"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    HUMOROUS = "humorous"


class ContentType(Enum):
    """Content types that can be generated"""
    EMAIL = "email"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    MARKETING_COPY = "marketing_copy"
    TECHNICAL_DOC = "technical_doc"
    STORY = "story"
    SCRIPT = "script"
    PRODUCT_DESC = "product_desc"


@dataclass
class ContentTemplate:
    """Template for content generation"""
    template_id: str
    content_type: ContentType
    tone: WritingTone
    template: str
    placeholders: List[str]
    
    def generate(self, values: Dict[str, str]) -> str:
        """Generate content from template"""
        result = self.template
        for placeholder, value in values.items():
            result = result.replace(f"{{{placeholder}}}", value)
        return result


@dataclass
class ABTestVariant:
    """A variant for A/B testing"""
    variant_id: str
    content: str
    impressions: int = 0
    conversions: int = 0
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate"""
        return self.conversions / self.impressions if self.impressions > 0 else 0.0


class CreativeWriter:
    """
    Creative content generation with tone adaptation and A/B testing.
    
    Features:
    - Multi-tone content generation
    - Template-based generation
    - A/B testing for creative outputs
    - Content optimization
    """
    
    def __init__(self):
        self.templates: Dict[str, ContentTemplate] = {}
        self.ab_tests: Dict[str, List[ABTestVariant]] = {}
        self.logger = logging.getLogger("CreativeWriter")
        self.logger.setLevel(logging.INFO)
        
        # Initialize default templates
        self._initialize_templates()
        
        self.logger.info("CreativeWriter initialized")
    
    def _initialize_templates(self):
        """Initialize default content templates"""
        
        # Email templates
        self.add_template(ContentTemplate(
            "email-professional",
            ContentType.EMAIL,
            WritingTone.PROFESSIONAL,
            """Dear {recipient},

I hope this message finds you well. I am writing to {purpose}.

{body}

Please let me know if you have any questions or require additional information.

Best regards,
{sender}""",
            ["recipient", "purpose", "body", "sender"]
        ))
        
        self.add_template(ContentTemplate(
            "email-casual",
            ContentType.EMAIL,
            WritingTone.CASUAL,
            """Hi {recipient},

{body}

Let me know what you think!

Cheers,
{sender}""",
            ["recipient", "body", "sender"]
        ))
        
        # Marketing copy templates
        self.add_template(ContentTemplate(
            "marketing-persuasive",
            ContentType.MARKETING_COPY,
            WritingTone.PERSUASIVE,
            """🚀 {headline}

{product} is the solution you've been waiting for!

✨ {benefit1}
✨ {benefit2}
✨ {benefit3}

{cta}""",
            ["headline", "product", "benefit1", "benefit2", "benefit3", "cta"]
        ))
        
        # Social media templates
        self.add_template(ContentTemplate(
            "social-friendly",
            ContentType.SOCIAL_MEDIA,
            WritingTone.FRIENDLY,
            """🎉 {announcement}

{description}

{hashtags}""",
            ["announcement", "description", "hashtags"]
        ))
    
    def add_template(self, template: ContentTemplate):
        """Add a content template"""
        self.templates[template.template_id] = template
        self.logger.debug(f"Added template: {template.template_id}")
    
    def generate_content(
        self,
        template_id: str,
        values: Dict[str, str],
        tone: Optional[WritingTone] = None
    ) -> str:
        """
        Generate content from a template.
        
        Args:
            template_id: Template to use
            values: Values for template placeholders
            tone: Optional tone override
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        content = template.generate(values)
        
        # Apply tone adjustments if different from template default
        if tone and tone != template.tone:
            content = self._adjust_tone(content, tone)
        
        self.logger.debug(f"Generated content using template: {template_id}")
        return content
    
    def _adjust_tone(self, content: str, target_tone: WritingTone) -> str:
        """Adjust content to match target tone"""
        # This is a simplified implementation
        # In a real system, this would use NLP techniques
        
        if target_tone == WritingTone.PROFESSIONAL:
            content = content.replace("!", ".")
            content = content.replace("...", ".")
        elif target_tone == WritingTone.CASUAL:
            content = content.replace("Dear", "Hi")
            content = content.replace("Best regards", "Thanks")
        elif target_tone == WritingTone.HUMOROUS:
            # Add some playful elements
            content = content.replace(".", " 😊")
        
        return content
    
    def generate_variations(
        self,
        base_content: str,
        count: int = 3,
        tone_variations: bool = True
    ) -> List[str]:
        """
        Generate multiple variations of content for A/B testing.
        
        Args:
            base_content: Original content
            count: Number of variations to generate
            tone_variations: Whether to vary tone
        """
        variations = [base_content]
        
        if tone_variations:
            tones = [WritingTone.PROFESSIONAL, WritingTone.CASUAL, WritingTone.CREATIVE]
            for i in range(min(count - 1, len(tones))):
                varied = self._adjust_tone(base_content, tones[i])
                variations.append(varied)
        
        # Generate additional variations with simple modifications
        while len(variations) < count:
            # Simple variation: add emphasis or modify punctuation
            variation = base_content
            if "!" not in variation:
                variation = variation.replace(".", "!", 1)
            variations.append(variation)
        
        return variations[:count]
    
    def create_ab_test(
        self,
        test_id: str,
        variants: List[str]
    ) -> Dict[str, Any]:
        """
        Create an A/B test with multiple variants.
        
        Args:
            test_id: Unique identifier for the test
            variants: List of content variants to test
        """
        test_variants = [
            ABTestVariant(f"{test_id}-variant-{i}", content)
            for i, content in enumerate(variants)
        ]
        
        self.ab_tests[test_id] = test_variants
        
        self.logger.info(f"Created A/B test: {test_id} with {len(variants)} variants")
        
        return {
            "test_id": test_id,
            "variant_count": len(variants),
            "variants": [v.variant_id for v in test_variants]
        }
    
    def get_variant(self, test_id: str, selection: str = "random") -> Optional[str]:
        """
        Get a variant from an A/B test.
        
        Args:
            test_id: Test identifier
            selection: Selection strategy ("random", "best", "round_robin")
        """
        if test_id not in self.ab_tests:
            return None
        
        variants = self.ab_tests[test_id]
        
        if selection == "random":
            variant = random.choice(variants)
        elif selection == "best":
            # Return variant with highest conversion rate
            variant = max(variants, key=lambda v: v.conversion_rate)
        else:  # round_robin
            # Simple round-robin based on impressions
            variant = min(variants, key=lambda v: v.impressions)
        
        variant.impressions += 1
        return variant.content
    
    def record_conversion(self, test_id: str, variant_content: str):
        """Record a conversion for a variant"""
        if test_id not in self.ab_tests:
            return
        
        for variant in self.ab_tests[test_id]:
            if variant.content == variant_content:
                variant.conversions += 1
                self.logger.debug(f"Recorded conversion for variant: {variant.variant_id}")
                break
    
    def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get results for an A/B test"""
        if test_id not in self.ab_tests:
            return None
        
        variants = self.ab_tests[test_id]
        
        return {
            "test_id": test_id,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "content": v.content,
                    "impressions": v.impressions,
                    "conversions": v.conversions,
                    "conversion_rate": v.conversion_rate
                }
                for v in variants
            ],
            "best_variant": max(variants, key=lambda v: v.conversion_rate).variant_id
            if variants else None
        }
    
    def list_templates(self, content_type: Optional[ContentType] = None) -> List[Dict[str, Any]]:
        """List available templates"""
        templates = []
        
        for template in self.templates.values():
            if content_type and template.content_type != content_type:
                continue
            
            templates.append({
                "template_id": template.template_id,
                "content_type": template.content_type.value,
                "tone": template.tone.value,
                "placeholders": template.placeholders
            })
        
        return templates
    
    def enhance_clarity(self, text: str) -> str:
        """
        Enhance text clarity (simplified implementation).
        
        In a real system, this would use NLP to:
        - Simplify complex sentences
        - Remove redundancy
        - Improve readability
        """
        # Simple clarity enhancements
        enhanced = text
        
        # Remove redundant spaces
        enhanced = " ".join(enhanced.split())
        
        # Ensure proper sentence capitalization
        sentences = enhanced.split(". ")
        enhanced = ". ".join(s.capitalize() for s in sentences)
        
        return enhanced

<#import "template.ftl" as layout>
<@layout.emailLayout>
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: #4F46E5; color: white; padding: 20px; text-align: center;">
        <h1 style="margin: 0;">Verdict360 Legal Platform</h1>
        <p style="margin: 5px 0 0 0;">Password Reset Request</p>
    </div>
    
    <div style="padding: 30px; background: #f9fafb;">
        <h2 style="color: #1E293B;">Reset Your Password</h2>
        <p>Hello ${user.firstName!""},</p>
        <p>You have requested to reset your password for your Verdict360 legal account. This is a secure legal platform, so please ensure you're the one making this request.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="${link}" style="background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
        </div>
        
        <p style="color: #6B7280; font-size: 14px;">This link will expire in ${linkExpiration}. If you did not request this password reset, please contact your system administrator immediately.</p>
        
        <p style="color: #6B7280; font-size: 14px;">For security reasons, please do not share this email with anyone.</p>
    </div>
    
    <div style="background: #1E293B; color: white; padding: 20px; text-align: center; font-size: 12px;">
        <p>&copy; ${.now?string("yyyy")} Verdict360. All rights reserved.</p>
        <p>This is an automated message from a secure legal platform.</p>
    </div>
</div>
</@layout.emailLayout>

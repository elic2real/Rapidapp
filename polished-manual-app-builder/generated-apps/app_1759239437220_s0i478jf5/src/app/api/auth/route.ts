import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const { email, password, action } = await request.json()

    if (action === 'login') {
      // Login logic
      const user = await prisma.user.findUnique({
        where: { email }
      })

      if (!user) {
        return NextResponse.json(
          { error: 'Invalid credentials' },
          { status: 401 }
        )
      }

      const isValidPassword = await bcrypt.compare(password, user.password)

      if (!isValidPassword) {
        return NextResponse.json(
          { error: 'Invalid credentials' },
          { status: 401 }
        )
      }

      // Remove password from response
      const { password: _, ...userWithoutPassword } = user

      return NextResponse.json({
        user: userWithoutPassword,
        message: 'Login successful'
      })
    }

    if (action === 'register') {
      // Check if user already exists
      const existingUser = await prisma.user.findUnique({
        where: { email }
      })

      if (existingUser) {
        return NextResponse.json(
          { error: 'User already exists' },
          { status: 400 }
        )
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 12)

      // Create user
      const user = await prisma.user.create({
        data: {
          email,
          password: hashedPassword,
        }
      })

      // Remove password from response
      const { password: _, ...userWithoutPassword } = user

      return NextResponse.json({
        user: userWithoutPassword,
        message: 'Registration successful'
      }, { status: 201 })
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    )
  } catch (error) {
    console.error('Auth error:', error)
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    )
  }
}